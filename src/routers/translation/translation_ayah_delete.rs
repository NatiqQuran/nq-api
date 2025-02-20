use crate::error::RouterError;
use crate::DbPool;
use ::uuid::Uuid;
use actix_web::web;
use diesel::prelude::*;
use serde::Deserialize;

#[derive(Deserialize)]
pub struct TextDeleteQuery {
    ayah_uuid: Uuid,
}

/// Delete single translation_ayah
pub async fn translation_ayah_delete(
    path: web::Path<Uuid>,
    pool: web::Data<DbPool>,
    query: web::Query<TextDeleteQuery>,
) -> Result<&'static str, RouterError> {
    use crate::schema::quran_ayahs::dsl::{id as ayah_id, quran_ayahs, uuid as ayah_uuid};
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
        let ayah: i32 = quran_ayahs
            .filter(ayah_uuid.eq(query.ayah_uuid))
            .select(ayah_id)
            .get_result(&mut conn)?;

        diesel::delete(
            quran_translations_ayahs
                .filter(text_ayah_id.eq(ayah))
                .filter(text_translation_id.eq(translation)),
        )
        .execute(&mut conn)?;

        Ok("Deleted")
    })
    .await
    .unwrap()
}
