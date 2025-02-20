use crate::error::RouterError;
use crate::DbPool;
use actix_web::web;
use diesel::prelude::*;
use uuid::Uuid;

use super::SimpleMushaf;

/// Update's single mushaf
pub async fn mushaf_edit(
    path: web::Path<Uuid>,
    new_mushaf: web::Json<SimpleMushaf>,
    pool: web::Data<DbPool>,
) -> Result<&'static str, RouterError> {
    use crate::schema::quran_mushafs::dsl::{
        name as mushaf_name, quran_mushafs, short_name as mushaf_short_name,
        source as mushaf_source, uuid as mushaf_uuid,
    };

    let new_mushaf = new_mushaf.into_inner();
    let target_mushaf_uuid = path.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        diesel::update(quran_mushafs.filter(mushaf_uuid.eq(target_mushaf_uuid)))
            .set((
                mushaf_name.eq(new_mushaf.name),
                mushaf_short_name.eq(new_mushaf.short_name),
                mushaf_source.eq(new_mushaf.source),
            ))
            .execute(&mut conn)?;

        Ok("Edited")
    })
    .await
    .unwrap()
}
