use std::str::FromStr;

use crate::error::RouterError;
use crate::models::{NewQuranAyah, NewQuranWord, QuranAyah};
use crate::DbPool;
use actix_web::web;
use diesel::prelude::*;
use serde::Deserialize;
use uuid::Uuid;

use super::Sajdah;

#[derive(Deserialize)]
pub struct AyahWithText {
    pub surah_uuid: String,
    pub sajdah: Option<Sajdah>,
    pub text: String,
    pub is_bismillah: bool,
    pub bismillah_text: Option<String>,
}

/// Add's a new ayah
pub async fn ayah_add(
    pool: web::Data<DbPool>,
    new_ayah: web::Json<AyahWithText>,
    data: web::ReqData<u32>,
) -> Result<&'static str, RouterError> {
    use crate::schema::app_users::dsl::{account_id as user_acc_id, app_users, id as user_id};
    use crate::schema::quran_ayahs::dsl::quran_ayahs;
    use crate::schema::quran_surahs::dsl::{id as surah_id, quran_surahs, uuid as surah_uuid};
    use crate::schema::quran_words::dsl::quran_words;

    let new_ayah = new_ayah.into_inner();
    let user_account_id = data.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // Creator user_id
        let user: i32 = app_users
            .filter(user_acc_id.eq(user_account_id as i32))
            .select(user_id)
            .get_result(&mut conn)?;

        // Get the target surah by surah-uuid
        let target_surah: i32 = quran_surahs
            .filter(surah_uuid.eq(Uuid::from_str(&new_ayah.surah_uuid)?))
            .select(surah_id)
            .get_result(&mut conn)?;

        // Calculate amount of ayahs in surah
        let latest_ayah_number: i64 = quran_ayahs
            .inner_join(quran_surahs)
            .filter(surah_id.eq(target_surah))
            .count()
            .get_result(&mut conn)?;

        // Insert new ayah
        let ayah: QuranAyah = NewQuranAyah {
            surah_id: target_surah,
            sajdah: new_ayah.sajdah.map(|sajdah| sajdah.to_string()),
            ayah_number: (latest_ayah_number + 1) as i32,
            creator_user_id: user,
            is_bismillah: new_ayah.is_bismillah,
            bismillah_text: new_ayah.bismillah_text,
        }
        .insert_into(quran_ayahs)
        .get_result(&mut conn)?;

        // Split the ayah text by space and insert them as quran_word
        let words: Vec<NewQuranWord> = new_ayah
            .text
            .split(' ')
            .map(|w| NewQuranWord {
                creator_user_id: user,
                word: w,
                ayah_id: ayah.id,
            })
            .collect();

        words.insert_into(quran_words).execute(&mut conn)?;

        Ok("Added")
    })
    .await
    .unwrap()
}
