use super::SurahName;
use super::{SurahListQuery, SurahListResponse};
use crate::error::RouterErrorDetailBuilder;
use crate::filter::Filter;
use crate::models::{QuranAyah, QuranMushaf, QuranSurah};
use crate::schema::quran_ayahs::surah_id;
use crate::{error::RouterError, DbPool};
use actix_web::{web, HttpRequest};
use diesel::dsl::count;
use diesel::prelude::*;

/// Get the lists of surah
pub async fn surah_list(
    query: web::Query<SurahListQuery>,
    pool: web::Data<DbPool>,
    req: HttpRequest,
) -> Result<web::Json<Vec<SurahListResponse>>, RouterError> {
    use crate::schema::app_phrase_translations::dsl::{
        app_phrase_translations, language as p_t_lang, text as p_t_text,
    };
    use crate::schema::app_phrases::dsl::{app_phrases, phrase as p_phrase};
    use crate::schema::quran_mushafs::dsl::{quran_mushafs, short_name as mushaf_name};
    use crate::schema::quran_surahs::dsl::*;

    let query = query.into_inner();
    let pool = pool.into_inner();

    let error_detail = RouterErrorDetailBuilder::from_http_request(&req).build();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // Select the specific mushaf
        // and check if it exists
        let mushaf = quran_mushafs
            .filter(mushaf_name.eq(&query.mushaf))
            .get_result::<QuranMushaf>(&mut conn)?;

        let filtered_surahs = match QuranSurah::filter(Box::from(query.clone())) {
            Ok(filtred) => filtred,
            Err(err) => return Err(err.log_to_db(pool, error_detail)),
        };

        // Get the list of surahs from the database
        let surahs = filtered_surahs
            .filter(mushaf_id.eq(mushaf.id))
            .load::<QuranSurah>(&mut conn)?;

        let ayahs = surahs
            .clone()
            .into_iter()
            .map(|s| {
                QuranAyah::belonging_to(&s)
                    .select(count(surah_id))
                    .get_result(&mut conn)
                    //TODO: remove unwrap
                    .unwrap()
            })
            .collect::<Vec<i64>>();

        // now iter over the surahs and bind it with
        // number_of_ayahs
        let surahs = surahs
            .into_iter()
            .zip(ayahs)
            .map(|(surah, number_of_ayahs)| {
                let translation = if let Some(ref phrase) = surah.name_translation_phrase {
                    let mut p = app_phrases.left_join(app_phrase_translations).into_boxed();

                    if let Some(ref l) = query.lang_code {
                        p = p.filter(p_t_lang.eq(l));
                    } else {
                        p = p.filter(p_t_lang.eq("en"));
                    }

                    p.filter(p_phrase.eq(phrase))
                        .select(p_t_text.nullable())
                        .get_result(&mut conn)
                        .unwrap()
                } else {
                    None
                };

                let surah_search_terms = surah.search_terms.map(|st| {
                    st.into_iter()
                        .map(|s| s.unwrap_or(String::new()))
                        .collect::<Vec<String>>()
                });

                SurahListResponse {
                    uuid: surah.uuid,
                    names: vec![SurahName {
                        arabic: surah.name,
                        translation,
                        translation_phrase: surah.name_translation_phrase,
                        pronunciation: surah.name_pronunciation,
                        transliteration: surah.name_transliteration,
                    }],
                    number: surah.number,
                    period: surah.period,
                    number_of_ayahs,
                    search_terms: surah_search_terms,
                }
            })
            .collect::<Vec<SurahListResponse>>();

        Ok(web::Json(surahs))
    })
    .await
    .unwrap()
}
