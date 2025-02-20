use crate::error::RouterError;
use crate::models::Translation;
use crate::{DbPool, TranslationAyah, TranslationStatus, TranslatorData, ViewableTranslation};
use ::uuid::Uuid;
use actix_web::web;
use diesel::{prelude::*, query_dsl::boxed_dsl::BoxedDsl};
use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub struct TranslationViewQuery {
    surah_uuid: Option<Uuid>,
}

/// Return's a single translation
pub async fn translation_view(
    path: web::Path<Uuid>,
    pool: web::Data<DbPool>,
    web::Query(query): web::Query<TranslationViewQuery>,
) -> Result<web::Json<ViewableTranslation>, RouterError> {
    use crate::schema::app_accounts::dsl::{
        app_accounts, id as account_table_id, username as acc_username, uuid as account_uuid,
    };
    use crate::schema::app_user_names::dsl::{
        app_user_names, first_name as user_first_name, last_name as user_last_name,
        primary_name as user_primary_name,
    };
    use crate::schema::quran_ayahs::dsl::{ayah_number, quran_ayahs, uuid as ayah_uuid};
    use crate::schema::quran_mushafs::dsl::{
        id as mushaf_table_id, quran_mushafs, uuid as mushaf_table_uuid,
    };
    use crate::schema::quran_surahs::dsl::{
        mushaf_id as surah_mushaf_id, number as surah_number, quran_surahs,
        uuid as surah_table_uuid,
    };
    use crate::schema::quran_translations::dsl::{quran_translations, uuid as translation_uuid};
    use crate::schema::quran_translations_ayahs::dsl::{
        bismillah as translation_ayah_bismillah, quran_translations_ayahs,
        text as translation_ayah, translation_id, uuid as translation_ayah_uuid,
    };

    let path = path.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // Get the single translation from the database
        let translation: Translation = quran_translations
            .filter(translation_uuid.eq(path))
            .get_result(&mut conn)?;

        let mushaf_uuid: Uuid = quran_mushafs
            .filter(mushaf_table_id.eq(translation.mushaf_id))
            .select(mushaf_table_uuid)
            .get_result(&mut conn)?;

        let translator = app_accounts
            .left_join(app_user_names)
            .filter(account_table_id.eq(translation.translator_account_id))
            .filter(user_primary_name.eq(true).or(user_primary_name.is_null()))
            .select((
                account_uuid,
                acc_username,
                user_first_name.nullable(),
                user_last_name.nullable(),
            ))
            .get_result::<(Uuid, String, Option<String>, Option<String>)>(&mut conn)?;

        let mut ayahs = quran_surahs
            .inner_join(quran_ayahs.left_outer_join(quran_translations_ayahs))
            .internal_into_boxed();

        if let Some(uuid) = query.surah_uuid {
            ayahs = ayahs.filter(surah_table_uuid.eq(uuid));
        }

        let result = ayahs
            .filter(surah_mushaf_id.eq(translation.mushaf_id))
            .filter(
                translation_id
                    .eq(translation.id)
                    .or(translation_id.is_null()),
            )
            .order(ayah_number.asc())
            .select((
                translation_ayah.nullable(),
                ayah_uuid,
                ayah_number,
                surah_number,
                translation_ayah_uuid.nullable(),
                translation_ayah_bismillah.nullable(),
            ))
            .get_results::<(Option<String>, Uuid, i32, i32, Option<Uuid>, Option<String>)>(
                &mut conn,
            )?;

        let mut result_ayahs = vec![];
        let mut status = TranslationStatus::Ok;

        for (text, a_uuid, a_number, s_number, text_uuid, bismillah) in result {
            if text_uuid.is_none() {
                status = TranslationStatus::Incomplete;
            }
            result_ayahs.push(TranslationAyah {
                uuid: a_uuid,
                text,
                surah_number: s_number as u32,
                number: a_number as u32,
                text_uuid,
                bismillah,
            });
        }

        if matches!(status, TranslationStatus::Ok) && !translation.approved {
            status = TranslationStatus::NotApproved;
        }

        Ok(web::Json(ViewableTranslation {
            ayahs: result_ayahs,
            status,
            source: translation.source,
            language: translation.language,
            release_date: translation.release_date,
            mushaf_uuid,
            translator: TranslatorData {
                account_uuid: translator.0,
                username: translator.1,
                first_name: translator.2,
                last_name: translator.3,
            },
        }))
    })
    .await
    .unwrap()
}
