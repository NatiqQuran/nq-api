use super::SimpleSurah;
use crate::error::RouterErrorDetail;
use crate::models::NewQuranSurah;
use crate::{error::RouterError, DbPool};
use actix_web::web;
use diesel::dsl::exists;
use diesel::prelude::*;

// Add's and new surah
pub async fn surah_add(
    new_surah: web::Json<SimpleSurah>,
    pool: web::Data<DbPool>,
    data: web::ReqData<u32>,
) -> Result<&'static str, RouterError> {
    use crate::schema::app_phrases::dsl::{app_phrases, phrase as phrase_text};
    use crate::schema::app_users::dsl::{account_id as user_acc_id, app_users, id as user_id};
    use crate::schema::quran_mushafs::dsl::{id as mushaf_id, quran_mushafs, uuid as mushaf_uuid};
    use crate::schema::quran_surahs::dsl::quran_surahs;

    let new_surah = new_surah.into_inner();
    let data = data.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // Select the mushaf by uuid
        // and get the mushaf id
        let mushaf: i32 = quran_mushafs
            .filter(mushaf_uuid.eq(new_surah.mushaf_uuid))
            .select(mushaf_id)
            .get_result(&mut conn)?;

        // Calculate amount of surahs in mushaf
        let latest_surah_number: i64 = quran_surahs
            .inner_join(quran_mushafs)
            .filter(mushaf_id.eq(mushaf))
            .count()
            .get_result(&mut conn)?;

        let user: i32 = app_users
            .filter(user_acc_id.eq(data as i32))
            .select(user_id)
            .get_result(&mut conn)?;

        if let Some(ref phrase) = new_surah.name_translation_phrase {
            let phrase_exists: bool =
                diesel::select(exists(app_phrases.filter(phrase_text.eq(phrase))))
                    .get_result(&mut conn)?;

            if !phrase_exists {
                return Err(RouterError::from_predefined("PHRASE_NOT_FOUND")
                    // TODO: FIX default
                    .log_to_db(pool.clone().into_inner(), RouterErrorDetail::default()))?;
            }
        }

        let search_terms = new_surah.search_terms.map(|v| {
            v.into_iter()
                .map(|s| Some(s))
                .collect::<Vec<Option<String>>>()
        });

        // Add a new surah
        NewQuranSurah {
            creator_user_id: user,
            name: new_surah.name,
            period: new_surah.period,
            number: (latest_surah_number + 1) as i32,
            mushaf_id: mushaf,
            name_pronunciation: new_surah.name_pronunciation,
            name_translation_phrase: new_surah.name_translation_phrase,
            name_transliteration: new_surah.name_transliteration,
            search_terms,
        }
        .insert_into(quran_surahs)
        .execute(&mut conn)?;

        Ok("Added")
    })
    .await
    .unwrap()
}
