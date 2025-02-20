use crate::error::RouterError;
use crate::models::NewQuranMushaf;
use crate::DbPool;
use actix_web::web;
use diesel::prelude::*;

use super::SimpleMushaf;

/// Add's new mushaf
pub async fn mushaf_add(
    new_mushaf: web::Json<SimpleMushaf>,
    pool: web::Data<DbPool>,
    data: web::ReqData<u32>,
) -> Result<&'static str, RouterError> {
    use crate::schema::app_users::dsl::{account_id as user_acc_id, app_users, id as user_id};
    use crate::schema::quran_mushafs::dsl::quran_mushafs;

    let new_mushaf = new_mushaf.into_inner();
    let data = data.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        let user: i32 = app_users
            .filter(user_acc_id.eq(data as i32))
            .select(user_id)
            .get_result(&mut conn)?;

        NewQuranMushaf {
            short_name: Some(&new_mushaf.short_name),
            creator_user_id: user,
            name: Some(&new_mushaf.name),
            source: Some(&new_mushaf.source),
        }
        .insert_into(quran_mushafs)
        .execute(&mut conn)?;

        Ok("Added")
    })
    .await
    .unwrap()
}
