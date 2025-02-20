use std::collections::HashMap;

use super::{
    AyahWord, Format, GetSurahQuery, QuranResponseData, SimpleAyah, SingleSurahResponse, SurahName,
};
use crate::models::{
    QuranAyah, QuranAyahBreaker, QuranMushaf, QuranSurah, QuranWord, QuranWordBreaker,
};
use crate::routers::multip;
use crate::routers::quran::word::WordBreaker;
use crate::{error::RouterError, DbPool};
use crate::{AyahBismillah, AyahTy, Breaker, SingleSurahMushaf};
use actix_web::web;
use diesel::prelude::*;
use uuid::Uuid;

/// View Surah
pub async fn surah_view(
    path: web::Path<Uuid>,
    query: web::Query<GetSurahQuery>,
    pool: web::Data<DbPool>,
) -> Result<web::Json<QuranResponseData>, RouterError> {
    use crate::schema::app_phrase_translations::dsl::{
        app_phrase_translations, language as p_t_lang, text as p_t_text,
    };
    use crate::schema::app_phrases::dsl::{app_phrases, phrase as p_phrase};
    use crate::schema::quran_ayahs::dsl::quran_ayahs;
    use crate::schema::quran_ayahs_breakers::dsl::quran_ayahs_breakers;
    use crate::schema::quran_mushafs::dsl::{id as mushaf_id, quran_mushafs};
    use crate::schema::quran_surahs::dsl::quran_surahs;
    use crate::schema::quran_surahs::dsl::uuid as surah_uuid;
    use crate::schema::quran_words::dsl::quran_words;
    use crate::schema::quran_words_breakers::dsl::quran_words_breakers;

    let query = query.into_inner();
    let requested_surah_uuid = path.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // [{ayah_id, name}...]
        // Also need to count name
        let breakers: Vec<QuranAyahBreaker> = quran_ayahs_breakers.get_results(&mut conn)?;
        let mut breakers = breakers.into_iter();

        let mut breakers_count: HashMap<String, u32> = HashMap::new();
        let mut map = HashMap::<i32, Vec<Breaker>>::new();

        while let Some(breaker) = breakers.next() {
            breakers_count
                .entry(breaker.name)
                .and_modify(|v| *v += 1)
                .or_insert(1);

            let val = breakers_count
                .clone()
                .into_iter()
                .map(|(k, v)| Breaker { name: k, number: v })
                .collect::<Vec<Breaker>>();

            map.entry(breaker.ayah_id).insert_entry(val);
        }

        let ayahs_words = quran_surahs
            .filter(surah_uuid.eq(requested_surah_uuid))
            .inner_join(
                quran_ayahs
                    .inner_join(quran_words)
                    .left_join(quran_ayahs_breakers),
            )
            .select((QuranAyah::as_select(), QuranWord::as_select()))
            .load::<(QuranAyah, QuranWord)>(&mut conn)?;

        let ayahs_words = ayahs_words
            .into_iter()
            .map(|(ayah, word)| {
                (
                    SimpleAyah {
                        id: ayah.id as u32,
                        uuid: ayah.uuid,
                        bismillah: AyahBismillah::from_ayah_fields(
                            ayah.is_bismillah,
                            ayah.bismillah_text,
                        ),
                        breakers: map.get(&ayah.id).clone().cloned(),
                        number: ayah.ayah_number as u32,
                        sajdah: ayah.sajdah,
                    },
                    word,
                )
            })
            .collect::<Vec<(SimpleAyah, QuranWord)>>();

        let ayahs_as_map = multip(ayahs_words, |a| a);

        let words_breakers = if matches!(query.format, Format::Word) {
            let breakers: Vec<QuranWordBreaker> = quran_words_breakers.get_results(&mut conn)?;
            let mut breakers = breakers.into_iter();
            // (i32)
            let mut collected_breakers: HashMap<i32, Vec<WordBreaker>> = HashMap::new();

            while let Some(breaker) = breakers.next() {
                collected_breakers
                    .entry(breaker.word_id)
                    .and_modify(|v| {
                        v.push(WordBreaker {
                            name: breaker.name.clone(),
                        })
                    })
                    .or_insert(vec![WordBreaker { name: breaker.name }]);
            }

            Some(collected_breakers)
        } else {
            None
        };

        let final_ayahs = ayahs_as_map
            .into_iter()
            .map(|(ayah, words)| match query.format {
                Format::Text => AyahTy::Text(crate::AyahWithText {
                    ayah,
                    text: words
                        .into_iter()
                        .map(|w| w.word)
                        .collect::<Vec<String>>()
                        .join(" "),
                }),
                Format::Word => AyahTy::Words(crate::AyahWithWords {
                    ayah: ayah.clone(),
                    words: words
                        .into_iter()
                        .map(|w| AyahWord {
                            breakers: words_breakers.clone().unwrap().get(&w.id).clone().cloned(),
                            word: w.word,
                        })
                        .collect(),
                }),
            })
            .collect::<Vec<AyahTy>>();

        // Get the surah
        let surah = quran_surahs
            .filter(surah_uuid.eq(requested_surah_uuid))
            .get_result::<QuranSurah>(&mut conn)?;

        // Get the mushaf
        let mushaf = quran_mushafs
            .filter(mushaf_id.eq(surah.mushaf_id))
            .get_result::<QuranMushaf>(&mut conn)?;

        let translation = if let Some(ref phrase) = surah.name_translation_phrase {
            let mut p = app_phrases.left_join(app_phrase_translations).into_boxed();

            if let Some(ref l) = query.lang_code {
                p = p.filter(p_t_lang.eq(l));
            } else {
                p = p.filter(p_t_lang.eq("en"));
            }

            p.filter(p_phrase.eq(phrase))
                .select(p_t_text.nullable())
                .get_result(&mut conn)?
        } else {
            None
        };
        let surah_search_terms = surah.search_terms.map(|st| {
            st.into_iter()
                .map(|s| s.unwrap_or(String::new()))
                .collect::<Vec<String>>()
        });

        Ok(web::Json(QuranResponseData {
            surah: SingleSurahResponse {
                mushaf: SingleSurahMushaf::from(mushaf),
                bismillah: final_ayahs.first().unwrap().format_bismillah_for_surah(),
                names: vec![SurahName {
                    arabic: surah.name,
                    translation,
                    translation_phrase: surah.name_translation_phrase,
                    pronunciation: surah.name_pronunciation,
                    transliteration: surah.name_transliteration,
                }],
                period: surah.period,
                number: surah.number as u32,
                number_of_ayahs: final_ayahs.len() as u32,
                search_terms: surah_search_terms,
            },
            ayahs: final_ayahs,
        }))
    })
    .await
    .unwrap()
}
