use crate::schema::{
    app_accounts, app_emails, app_organizations, app_tokens, app_users, app_verify_codes,
};
use chrono::{NaiveDate, NaiveDateTime};
use diesel::{Associations, Identifiable, Insertable, Queryable};
use serde::{Deserialize, Serialize};
use validator::Validate;

#[derive(Identifiable, Queryable, Debug)]
#[diesel(table_name = app_accounts)]
pub struct Account {
    pub id: i32,
    pub username: String,
    pub account_type: String,
}

#[derive(Insertable)]
#[diesel(table_name = app_accounts)]
pub struct NewAccount<'a> {
    pub username: &'a String,
    pub account_type: &'a String,
}

#[derive(Identifiable, Queryable, Debug)]
#[diesel(table_name = app_verify_codes)]
pub struct VerifyCode {
    pub id: i32,
    pub code: i32,
    pub email: String,
    pub status: String,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = app_verify_codes)]
pub struct NewVerifyCode<'a> {
    pub status: &'a String,
    pub code: &'a i32,
    pub email: &'a String,
}

#[derive(Associations, Identifiable, Queryable, Debug, Clone, Serialize)]
#[diesel(belongs_to(Account))]
#[diesel(table_name = app_users)]
pub struct User {
    pub id: i32,
    pub account_id: i32,
    pub first_name: Option<String>,
    pub last_name: Option<String>,
    pub birthday: Option<NaiveDateTime>,
    pub profile_image: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Queryable, Debug, Clone, Serialize)]
pub struct UserProfile {
    pub username: String,
    pub first_name: Option<String>,
    pub last_name: Option<String>,
    pub birthday: Option<NaiveDateTime>,
    pub profile_image: Option<String>,
}

#[derive(Insertable)]
#[diesel(table_name = app_users)]
pub struct NewUser {
    pub account_id: i32,
}

// TODO: use belongs to
#[derive(Identifiable, Queryable, Debug, Clone)]
#[diesel(table_name = app_tokens)]
pub struct Token {
    pub id: i32,
    pub user_id: i32,
    pub token_hash: String,
    pub terminated: bool,
    pub teminated_by_id: i32,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = app_tokens)]
pub struct NewToken<'a> {
    pub user_id: &'a i32,
    pub token_hash: &'a String,
}

#[derive(Queryable, PartialEq, Eq, Debug, Serialize, Deserialize)]
pub struct QuranText {
    id: i32,
    surah: i32,
    verse: i32,
    text: String,
}

#[derive(Identifiable, Queryable, Associations, PartialEq, Debug)]
#[diesel(belongs_to(Account))]
#[diesel(table_name = app_emails)]
pub struct Email {
    pub id: i32,
    pub account_id: i32,
    pub email: String,
    pub verified: bool,
    pub primary: bool,
    pub deleted: bool,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = app_emails)]
pub struct NewEmail<'a> {
    pub account_id: i32,
    pub email: &'a String,
    pub verified: bool,
    pub primary: bool,
    pub deleted: bool,
}

#[derive(Identifiable, Associations, Queryable, PartialEq, Debug, Serialize, Clone)]
#[diesel(belongs_to(Account))]
#[diesel(table_name = app_organizations)]
pub struct Organization {
    pub id: i32,
    pub account_id: i32,
    pub name: String,
    pub profile_image: Option<String>,
    pub established_date: NaiveDate,
    pub national_id: String,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable, Deserialize, Validate)]
#[diesel(table_name = app_organizations)]
pub struct NewOrganization {
    pub account_id: i32,
    pub name: String,
    pub profile_image: Option<String>,
    pub established_date: NaiveDate,
    pub national_id: String,
}
