use crate::error::RouterError;
use crate::{AyahBismillah, DbPool};
use actix_web::web;
use diesel::prelude::*;
use uuid::Uuid;

use super::SimpleAyah;

/// Update's single ayah
pub async fn ayah_edit(
    path: web::Path<Uuid>,
    new_ayah: web::Json<SimpleAyah>,
    pool: web::Data<DbPool>,
) -> Result<&'static str, RouterError> {
    use crate::schema::quran_ayahs::dsl::{
        ayah_number, bismillah_text, is_bismillah, quran_ayahs, sajdah as ayah_sajdah,
        uuid as ayah_uuid,
    };

    let new_ayah = new_ayah.into_inner();
    let target_ayah_uuid = path.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        let new_sajdah = new_ayah.sajdah.map(|sajdah| sajdah.to_string());

        diesel::update(quran_ayahs.filter(ayah_uuid.eq(target_ayah_uuid)))
            .set((
                ayah_number.eq(new_ayah.ayah_number),
                ayah_sajdah.eq(new_sajdah),
                is_bismillah.eq(new_ayah
                    .bismillah
                    .clone()
                    .unwrap_or(AyahBismillah {
                        is_ayah: false,
                        text: None,
                    })
                    .is_ayah),
                bismillah_text.eq(new_ayah
                    .bismillah
                    .unwrap_or(AyahBismillah {
                        is_ayah: false,
                        text: None,
                    })
                    .text),
            ))
            .execute(&mut conn)?;

        Ok("Edited")
    })
    .await
    .unwrap()
}
