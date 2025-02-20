use crate::error::RouterError;
use crate::models::TranslationAyah;
use crate::DbPool;
use ::uuid::Uuid;
use actix_web::web;
use diesel::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct TextViewQuery {
    pub ayah_uuid: Uuid,
}

#[derive(Deserialize, Serialize)]
pub struct TranslationAyahData {
    pub uuid: Uuid,
    pub text: String,
    pub bismillah: Option<String>,
    pub has_bismillah: bool,
}

/// Return's a single translation_ayah
pub async fn translation_ayah_view(
    path: web::Path<Uuid>,
    pool: web::Data<DbPool>,
    query: web::Query<TextViewQuery>,
) -> Result<web::Json<TranslationAyahData>, RouterError> {
    use crate::schema::quran_ayahs::dsl::{
        bismillah_text, id as ayah_id, quran_ayahs, uuid as ayah_uuid,
    };
    use crate::schema::quran_translations::dsl::{
        id as translations_id, quran_translations, uuid as translation_uuid,
    };
    use crate::schema::quran_translations_ayahs::dsl::{
        ayah_id as text_ayah_id, quran_translations_ayahs, translation_id as text_translation_id,
    };

    let path = path.into_inner();
    let query = query.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // Get the translation by uuid
        let translation: i32 = quran_translations
            .filter(translation_uuid.eq(path))
            .select(translations_id)
            .get_result(&mut conn)?;

        // Get the ayah by uuid
        let (a_id, a_bismillah_text): (i32, Option<String>) = quran_ayahs
            .filter(ayah_uuid.eq(query.ayah_uuid))
            .select((ayah_id, bismillah_text))
            .get_result(&mut conn)?;

        // Get the single translation_ayah from the database
        let translation_ayah: TranslationAyah = quran_translations_ayahs
            .filter(text_ayah_id.eq(a_id))
            .filter(text_translation_id.eq(translation))
            .get_result(&mut conn)?;

        Ok(web::Json(TranslationAyahData {
            uuid: translation_ayah.uuid,
            text: translation_ayah.text,
            bismillah: translation_ayah.bismillah,
            has_bismillah: a_bismillah_text.is_some(),
        }))
    })
    .await
    .unwrap()
}
