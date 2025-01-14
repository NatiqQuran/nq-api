use crate::error::{RouterError, RouterErrorDetailBuilder};
use crate::filter::Filter;
use crate::models::Translation;
use crate::DbPool;
use actix_web::{web, HttpRequest};
use chrono::NaiveDate;
use diesel::prelude::*;
use serde::Serialize;
use uuid::Uuid;

use super::TranslationListQuery;

#[derive(Serialize)]
pub struct TranslatorData {
    account_uuid: Uuid,
    username: String,
    first_name: Option<String>,
    last_name: Option<String>,
}

#[derive(Serialize)]
pub struct TranslationItem {
    pub uuid: Uuid,

    pub language: String,
    pub release_date: Option<NaiveDate>,
    pub source: Option<String>,

    /// translation content status
    pub approved: bool,

    pub translator: TranslatorData,
}

/// Returns the list of translations
pub async fn translation_list(
    pool: web::Data<DbPool>,
    web::Query(query): web::Query<TranslationListQuery>,
    req: HttpRequest,
) -> Result<web::Json<Vec<TranslationItem>>, RouterError> {
    use crate::schema::app_accounts::dsl::{
        app_accounts, username as acc_username, uuid as acc_uuid,
    };
    use crate::schema::app_user_names::dsl::{
        app_user_names, first_name as user_first_name, last_name as user_last_name,
        primary_name as user_primary_name,
    };
    use crate::schema::quran_mushafs::dsl::{
        id as mushaf_id, quran_mushafs, short_name as mushaf_short_name,
    };
    use crate::schema::quran_translations::dsl::{
        language as translation_lang, mushaf_id as translation_mushaf_id,
    };

    let pool = pool.into_inner();

    let error_detail = RouterErrorDetailBuilder::from_http_request(&req).build();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        let mushafid: i32 = quran_mushafs
            .filter(mushaf_short_name.eq(query.mushaf.clone()))
            .select(mushaf_id)
            .get_result(&mut conn)?;

        // Get the list of translations from the database
        let mut translations_list = match Translation::filter(Box::from(query.clone())) {
            Ok(filtred) => filtred,
            Err(err) => return Err(err.log_to_db(pool, error_detail)),
        };

        if let Some(lang) = query.language {
            translations_list = translations_list.filter(translation_lang.eq(lang));
        }

        let translations_list = if let Some(translator_uuid) = query.translator_account_uuid {
            translations_list
                .inner_join(app_accounts.left_join(app_user_names))
                .filter(translation_mushaf_id.eq(mushafid))
                .filter(acc_uuid.eq(translator_uuid))
                .filter(user_primary_name.eq(true).or(user_primary_name.is_null()))
                .select((
                    Translation::as_select(),
                    acc_uuid,
                    acc_username,
                    user_first_name.nullable(),
                    user_last_name.nullable(),
                ))
                .get_results(&mut conn)?
                .into_iter()
                .map(
                    |(t, a_u, username, first_name, last_name)| TranslationItem {
                        uuid: t.uuid,
                        source: t.source,
                        language: t.language,
                        approved: t.approved,
                        release_date: t.release_date,
                        translator: TranslatorData {
                            account_uuid: a_u,
                            username,
                            last_name,
                            first_name,
                        },
                    },
                )
                .collect()
        } else {
            translations_list
                .inner_join(app_accounts.left_join(app_user_names))
                .filter(translation_mushaf_id.eq(mushafid))
                .filter(user_primary_name.eq(true).or(user_primary_name.is_null()))
                .select((
                    Translation::as_select(),
                    acc_uuid,
                    acc_username,
                    user_first_name.nullable(),
                    user_last_name.nullable(),
                ))
                .get_results(&mut conn)?
                .into_iter()
                .map(
                    |(t, a_u, username, first_name, last_name)| TranslationItem {
                        uuid: t.uuid,
                        source: t.source,
                        language: t.language,
                        approved: t.approved,
                        release_date: t.release_date,
                        translator: TranslatorData {
                            account_uuid: a_u,
                            username,
                            last_name,
                            first_name,
                        },
                    },
                )
                .collect()
        };

        Ok(web::Json(translations_list))
    })
    .await
    .unwrap()
}
