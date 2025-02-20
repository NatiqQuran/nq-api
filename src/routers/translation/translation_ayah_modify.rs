use crate::translation_ayah_view::TextViewQuery;
use crate::{error::RouterError, models::NewTranslationAyah, DbPool};
use actix_web::web;
use diesel::select;
use diesel::{dsl::exists, prelude::*};
use uuid::Uuid;

use super::SimpleTranslationAyah;

/// Modify translation text,
///
/// If the translation to an ayah exists updated it,
/// otherwise add.
pub async fn translation_ayah_modify(
    new_translation_ayah: web::Json<SimpleTranslationAyah>,
    pool: web::Data<DbPool>,
    data: web::ReqData<u32>,
    // translatio uuid
    path: web::Path<Uuid>,
    query: web::Query<TextViewQuery>,
) -> Result<&'static str, RouterError> {
    use crate::schema::app_users::dsl::{account_id as user_acc_id, app_users, id as user_id};
    use crate::schema::quran_ayahs::dsl::{
        bismillah_text, id as ayah_id, quran_ayahs, uuid as ayah_uuid,
    };
    use crate::schema::quran_translations::dsl::{
        id as translation_id, quran_translations, uuid as translation_uuid,
    };
    use crate::schema::quran_translations_ayahs::dsl::{
        ayah_id as text_ayah_id, bismillah as translation_ayah_bismillah, quran_translations_ayahs,
        text as text_content, translation_id as text_translation_id,
    };

    let new_translation_ayah = new_translation_ayah.into_inner();
    let path = path.into_inner();
    let creator_id = data.into_inner();
    let query = query.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // Get the target translation
        let translation: i32 = quran_translations
            .filter(translation_uuid.eq(path))
            .select(translation_id)
            .get_result(&mut conn)?;

        // Get the translation text ayah id
        let (a_id, a_bismillah_text): (i32, Option<String>) = quran_ayahs
            .filter(ayah_uuid.eq(query.ayah_uuid))
            .select((ayah_id, bismillah_text))
            .get_result(&mut conn)?;

        if a_bismillah_text.is_none() && new_translation_ayah.bismillah.is_some() {
            return Err(RouterError::from_predefined("NO_BISMILLAH"));
        }

        // Now check if the translation_ayah exists
        let text: bool = select(exists(
            quran_translations_ayahs
                .filter(text_ayah_id.eq(a_id))
                .filter(text_translation_id.eq(translation)),
        ))
        .get_result(&mut conn)?;

        // TODO: use (on conflict do update)
        if text {
            // This means the translation_ayah exists, we just need to update it
            diesel::update(quran_translations_ayahs)
                .filter(text_ayah_id.eq(a_id))
                .filter(text_translation_id.eq(translation))
                .set((
                    text_content.eq(new_translation_ayah.text),
                    translation_ayah_bismillah.eq(new_translation_ayah.bismillah),
                ))
                .execute(&mut conn)?;

            Ok("Updated")
        } else {
            // Get the userId from users account id
            let user: i32 = app_users
                .filter(user_acc_id.eq(creator_id as i32))
                .select(user_id)
                .get_result(&mut conn)?;

            // This means user wants to add a new translation_ayah
            NewTranslationAyah {
                creator_user_id: user,
                text: &new_translation_ayah.text,
                translation_id: translation,
                ayah_id: a_id,
                bismillah: new_translation_ayah.bismillah,
            }
            .insert_into(quran_translations_ayahs)
            .execute(&mut conn)?;

            Ok("Added")
        }
    })
    .await
    .unwrap()
}
