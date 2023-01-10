use crate::{
    models::{Account, Organization},
    DbPool,
};
use actix_web::{web, Responder};
use diesel::prelude::*;
use diesel::result::Error;
use serde::Deserialize;

#[derive(Deserialize)]
pub struct OrgInfoUpdatebleFileds {
    username: String,
    name: String,
    profile_image: Option<String>,
    national_id: String,
}

/// Edits the org
pub async fn edit_organization(
    path: web::Path<u32>,
    info: web::Json<OrgInfoUpdatebleFileds>,
    pool: web::Data<DbPool>,
) -> impl Responder {
    use crate::schema::app_accounts::dsl::{app_accounts, id as account_id, username};
    use crate::schema::app_organizations::dsl::*;

    let org_id = path.into_inner();
    let new_org = info.into_inner();

    let update_result: Result<(), Error> = web::block(move || {
        let mut conn = pool.get().unwrap();

        // First find the org from id
        let account = app_accounts
            .filter(account_id.eq(org_id as i32))
            .load::<Account>(&mut conn)?;

        let org =
            Organization::belonging_to(account.get(0).unwrap()).load::<Organization>(&mut conn)?;

        let account = account.get(0).unwrap();
        let org = org.get(0).unwrap();

        diesel::update(account)
            .set(username.eq(new_org.username))
            .execute(&mut conn)?;

        diesel::update(&org)
            .set((
                name.eq(new_org.name),
                profile_image.eq(new_org.profile_image),
                national_id.eq(new_org.national_id),
            ))
            .execute(&mut conn)?;

        Ok(())
    })
    .await
    .unwrap();

    match update_result {
        Ok(()) => "Updated",

        // TODO: handle database errors
        Err(_error) => "error",
    }
}
