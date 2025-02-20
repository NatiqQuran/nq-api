use crate::schema::*;
use chrono::{NaiveDate, NaiveDateTime};
use diesel::{
    deserialize::QueryableByName, Associations, Identifiable, Insertable, Queryable, Selectable,
};
use ipnetwork::IpNetwork;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use validator::Validate;

#[derive(Selectable, Identifiable, Queryable, Debug, Serialize)]
#[diesel(table_name = app_accounts)]
pub struct Account {
    pub id: i32,
    pub uuid: Uuid,
    pub username: String,
    pub account_type: String,
}

#[derive(Insertable)]
#[diesel(table_name = app_accounts)]
pub struct NewAccount<'a> {
    pub username: &'a String,
    pub account_type: &'a String,
}

#[derive(Clone, Identifiable, Queryable, Debug, Serialize, Associations, Selectable)]
#[diesel(belongs_to(Account))]
#[diesel(table_name = app_user_names)]
pub struct UserName {
    pub id: i32,
    pub account_id: i32,
    pub creator_user_id: i32,
    pub primary_name: bool,
    pub first_name: String,
    pub last_name: String,
    pub language: String,
}

#[derive(Insertable)]
#[diesel(table_name = app_user_names)]
pub struct NewUserNames {
    pub account_id: i32,
    pub primary_name: bool,
    pub creator_user_id: i32,
    pub first_name: Option<String>,
    pub last_name: Option<String>,
    pub language: Option<String>,
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

#[derive(Associations, Identifiable, Queryable, Debug, Clone, Serialize, Selectable)]
#[diesel(belongs_to(Account))]
#[diesel(table_name = app_users)]
pub struct User {
    #[serde(skip_serializing)]
    pub id: i32,

    #[serde(skip_serializing)]
    pub account_id: i32,

    pub birthday: Option<NaiveDate>,
    pub profile_image: Option<String>,
    pub language: Option<String>,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Queryable, Debug, Clone, Serialize, Deserialize)]
pub struct UserProfile {
    pub username: String,
    pub first_name: Option<String>,
    pub last_name: Option<String>,
    pub birthday: Option<NaiveDate>,
    pub profile_image: Option<String>,
    pub language: String,
}

#[derive(Insertable)]
#[diesel(table_name = app_users)]
pub struct NewUser {
    pub birthday: Option<NaiveDate>,
    pub account_id: i32,
    pub language: Option<String>,
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

#[derive(Queryable, Insertable)]
#[diesel(table_name = app_tokens)]
pub struct NewToken<'a> {
    pub account_id: i32,
    pub token_hash: &'a str,
}

#[derive(Identifiable, Queryable, Associations, PartialEq, Debug, Clone)]
#[diesel(belongs_to(Account))]
#[diesel(table_name = app_emails)]
pub struct Email {
    pub id: i32,
    pub account_id: i32,
    pub creator_user_id: i32,
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
    pub creator_user_id: i32,
    pub email: &'a String,
    pub verified: bool,
    pub primary: bool,
    pub deleted: bool,
}

#[derive(Selectable, Identifiable, Associations, Queryable, PartialEq, Debug, Serialize, Clone)]
#[diesel(belongs_to(Account, foreign_key = account_id))]
#[diesel(table_name = app_organizations)]
pub struct Organization {
    pub id: i32,
    pub account_id: i32,
    pub owner_account_id: i32,
    pub creator_user_id: i32,
    pub profile_image: Option<String>,
    pub established_date: NaiveDate,
    pub national_id: String,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Selectable, Clone, Identifiable, Queryable, Debug, Serialize, Associations)]
#[diesel(belongs_to(Account))]
#[diesel(table_name = app_organization_names)]
pub struct OrganizationName {
    #[serde(skip_serializing)]
    pub id: i32,
    pub uuid: Uuid,
    pub creator_user_id: i32,

    #[serde(skip_serializing)]
    pub account_id: i32,
    pub name: String,
    pub language: String,
}

#[derive(Insertable)]
#[diesel(table_name = app_organization_names)]
pub struct NewOrganizationName {
    pub creator_user_id: i32,
    pub account_id: i32,
    pub name: String,
    pub language: String,
}

#[derive(Insertable, Deserialize, Validate)]
#[diesel(table_name = app_organizations)]
pub struct NewOrganization {
    pub creator_user_id: i32,
    pub account_id: i32,
    pub owner_account_id: i32,
    pub profile_image: Option<String>,
    pub established_date: NaiveDate,
    pub national_id: String,
}

#[derive(Queryable, Deserialize, Validate)]
#[diesel(table_name = app_employees)]
pub struct Employee {
    pub id: i32,
    pub org_account_id: i32,
    pub creator_user_id: i32,
    pub employee_account_id: i32,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable, Deserialize, Validate)]
#[diesel(table_name = app_employees)]
pub struct NewEmployee {
    pub org_account_id: i32,
    pub creator_user_id: i32,
    pub employee_account_id: i32,
}

#[derive(
    Selectable,
    Insertable,
    Deserialize,
    Validate,
    Queryable,
    Identifiable,
    Serialize,
    Associations,
    Clone,
    Debug,
    Eq,
    Ord,
    PartialOrd,
    Hash,
    PartialEq,
)]
#[diesel(belongs_to(QuranSurah, foreign_key = surah_id))]
#[diesel(table_name = quran_ayahs)]
pub struct QuranAyah {
    #[serde(skip_serializing)]
    pub id: i32,
    pub uuid: Uuid,
    #[serde(skip_serializing)]
    pub creator_user_id: i32,

    #[serde(skip_serializing)]
    pub surah_id: i32,

    pub ayah_number: i32,
    pub sajdah: Option<String>,
    pub is_bismillah: bool,
    pub bismillah_text: Option<String>,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = quran_ayahs)]
pub struct NewQuranAyah {
    pub creator_user_id: i32,
    pub surah_id: i32,
    pub ayah_number: i32,
    pub sajdah: Option<String>,
    pub is_bismillah: bool,
    pub bismillah_text: Option<String>,
}

#[derive(
    Clone,
    Selectable,
    Identifiable,
    Associations,
    Queryable,
    PartialEq,
    Debug,
    Serialize,
    Hash,
    Ord,
    PartialOrd,
    Eq,
)]
#[diesel(belongs_to(QuranAyah, foreign_key = ayah_id))]
#[diesel(table_name = quran_words)]
pub struct QuranWord {
    #[serde(skip_serializing)]
    pub id: i32,
    pub uuid: Uuid,
    pub creator_user_id: i32,

    #[serde(skip_serializing)]
    pub ayah_id: i32,

    pub word: String,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = quran_words)]
pub struct NewQuranWord<'a> {
    pub creator_user_id: i32,
    pub ayah_id: i32,
    pub word: &'a str,
}

#[derive(Deserialize, Serialize, Clone, Validate, Identifiable, Queryable, Selectable, Debug)]
#[diesel(belongs_to(QuranMushaf, foreign_key = mushaf_id))]
#[diesel(table_name = quran_surahs)]
pub struct QuranSurah {
    #[serde(skip_serializing)]
    pub id: i32,
    pub uuid: Uuid,

    pub creator_user_id: i32,

    pub name: String,
    pub period: Option<String>,
    pub number: i32,
    pub mushaf_id: i32,

    pub name_pronunciation: Option<String>,
    pub name_translation_phrase: Option<String>,

    pub name_transliteration: Option<String>,

    pub search_terms: Option<Vec<Option<String>>>,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = quran_surahs)]
pub struct NewQuranSurah {
    pub creator_user_id: i32,
    pub name: String,
    pub period: Option<String>,
    pub number: i32,
    pub mushaf_id: i32,
    pub name_pronunciation: Option<String>,
    pub name_translation_phrase: Option<String>,
    pub name_transliteration: Option<String>,
    pub search_terms: Option<Vec<Option<String>>>,
}

#[derive(Deserialize, Serialize, Clone, Validate, Identifiable, Queryable, Selectable, Debug)]
#[diesel(table_name = quran_mushafs)]
pub struct QuranMushaf {
    #[serde(skip_serializing)]
    pub id: i32,
    pub uuid: Uuid,
    #[serde(skip_serializing)]
    pub creator_user_id: i32,

    pub short_name: Option<String>,
    pub name: Option<String>,
    pub source: Option<String>,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = quran_mushafs)]
pub struct NewQuranMushaf<'a> {
    pub creator_user_id: i32,
    pub short_name: Option<&'a str>,
    pub name: Option<&'a str>,
    pub source: Option<&'a str>,
}

#[derive(Deserialize, Serialize, Clone, Validate, Identifiable, Queryable, Debug, Selectable)]
#[diesel(table_name = app_permissions)]
#[diesel(belongs_to(Account))]
pub struct Permission {
    #[serde(skip_serializing)]
    pub id: i32,
    pub uuid: Uuid,

    pub creator_user_id: i32,

    pub account_id: i32,
    pub object: String,
    pub action: String,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = app_permissions)]
pub struct NewPermission<'a> {
    pub creator_user_id: i32,
    pub account_id: i32,
    pub object: &'a String,
    pub action: &'a String,
}

#[derive(
    Deserialize,
    Serialize,
    Clone,
    Validate,
    Identifiable,
    Queryable,
    Debug,
    Associations,
    Selectable,
)]
#[diesel(belongs_to(Permission))]
#[diesel(table_name = app_permission_conditions)]
pub struct PermissionCondition {
    #[serde(skip_serializing)]
    pub id: i32,
    pub uuid: Uuid,

    pub creator_user_id: i32,

    #[serde(skip_serializing)]
    pub permission_id: i32,

    pub name: String,
    pub value: String,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = app_permission_conditions)]
pub struct NewPermissionCondition {
    pub creator_user_id: i32,
    pub permission_id: i32,
    pub name: String,
    pub value: String,
}

#[derive(
    Deserialize,
    Serialize,
    Clone,
    Validate,
    Identifiable,
    Queryable,
    Debug,
    Selectable,
    Associations,
)]
#[diesel(table_name = quran_translations)]
#[diesel(belongs_to(Account, foreign_key = translator_account_id))]
pub struct Translation {
    #[serde(skip_serializing)]
    pub id: i32,
    pub uuid: Uuid,

    #[serde(skip_serializing)]
    pub mushaf_id: i32,

    #[serde(skip_serializing)]
    pub creator_user_id: i32,

    #[serde(skip_serializing)]
    pub translator_account_id: i32,

    pub language: String,
    pub release_date: Option<NaiveDate>,
    pub source: Option<String>,

    /// translation content status
    pub approved: bool,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = quran_translations)]
pub struct NewTranslation {
    pub creator_user_id: i32,
    pub translator_account_id: i32,

    pub language: String,
    pub release_date: Option<NaiveDate>,
    pub source: Option<String>,
}

#[derive(
    Deserialize,
    Serialize,
    Clone,
    Validate,
    Identifiable,
    Queryable,
    Debug,
    Associations,
    Selectable,
    QueryableByName,
)]
#[diesel(table_name = quran_translations_ayahs)]
#[diesel(belongs_to(Translation))]
#[diesel(belongs_to(QuranAyah, foreign_key = ayah_id))]
pub struct TranslationAyah {
    #[serde(skip_serializing)]
    pub id: i32,
    pub uuid: Uuid,

    #[serde(skip_serializing)]
    pub creator_user_id: i32,

    #[serde(skip_serializing)]
    pub translation_id: i32,

    #[serde(skip_serializing)]
    pub ayah_id: i32,

    pub text: String,

    /// Translated Bissmillah
    #[serde(skip_serializing)]
    pub bismillah: Option<String>,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = quran_translations_ayahs)]
pub struct NewTranslationAyah<'a> {
    pub creator_user_id: i32,
    pub translation_id: i32,
    pub ayah_id: i32,
    pub text: &'a String,
    pub bismillah: Option<String>,
}

#[derive(Deserialize, Serialize, Clone, Validate, Identifiable, Queryable, Debug, Selectable)]
#[diesel(table_name = app_error_logs)]
pub struct ErrorLog {
    pub id: i32,
    pub uuid: Uuid,
    pub error_name: String,
    pub status_code: i32,
    pub message: String,
    pub detail: Option<String>,
    pub account_id: Option<i32>,
    pub request_token: Option<String>,
    pub request_user_agent: Option<String>,
    pub request_ipv4: IpNetwork,
    pub request_url: Option<String>,
    pub request_controller: Option<String>,
    pub request_action: Option<String>,
    pub request_id: Option<String>,
    pub request_body: Option<Vec<u8>>,
    pub request_body_content_type: Option<String>,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = app_error_logs)]
pub struct NewErrorLog<'a> {
    pub error_name: &'a String,
    pub status_code: i32,
    pub message: &'a String,
    pub detail: Option<&'a String>,
    pub request_user_agent: Option<&'a String>,
    pub request_ipv4: IpNetwork,
    pub account_id: Option<i32>,
    pub request_token: Option<String>,
    pub request_url: Option<String>,
    pub request_controller: Option<String>,
    pub request_action: Option<String>,
    pub request_id: Option<String>,
    pub request_body: Option<Vec<u8>>,
    pub request_body_content_type: Option<String>,
}

#[derive(Deserialize, Serialize, Clone, Validate, Identifiable, Queryable, Debug, Selectable)]
#[diesel(table_name = app_phrases)]
pub struct Phrase {
    #[serde(skip_serializing)]
    id: i32,
    uuid: Uuid,

    phrase: String,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = app_phrases)]
pub struct NewPhrase<'a> {
    pub phrase: &'a str,
}

#[derive(
    Deserialize,
    Serialize,
    Clone,
    Validate,
    Identifiable,
    Queryable,
    Debug,
    Associations,
    Selectable,
    QueryableByName,
)]
#[diesel(table_name = app_phrase_translations)]
#[diesel(belongs_to(Phrase))]
pub struct PhraseTranslation {
    #[serde(skip_serializing)]
    id: i32,
    uuid: Uuid,

    #[serde(skip_serializing)]
    phrase_id: i32,

    text: String,
    language: String,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(Insertable)]
#[diesel(table_name = app_phrase_translations)]
pub struct NewPhraseTranslation<'a> {
    pub phrase_id: i32,
    pub text: &'a str,
    pub language: &'a str,
}

#[derive(
    Deserialize,
    Serialize,
    Clone,
    Validate,
    Identifiable,
    Queryable,
    Debug,
    Associations,
    Selectable,
    Eq,
    Hash,
    PartialEq,
)]
#[diesel(table_name = quran_ayahs_breakers)]
#[diesel(belongs_to(QuranAyah, foreign_key = ayah_id))]
pub struct QuranAyahBreaker {
    #[serde(skip_serializing)]
    id: i32,
    uuid: Uuid,

    #[serde(skip_serializing)]
    creator_user_id: i32,

    #[serde(skip_serializing)]
    pub ayah_id: i32,

    #[serde(skip_serializing)]
    owner_account_id: Option<i32>,

    pub name: String,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}

#[derive(
    Deserialize,
    Serialize,
    Clone,
    Validate,
    Identifiable,
    Queryable,
    Debug,
    Associations,
    Selectable,
    PartialEq,
    Eq,
    Hash,
)]
#[diesel(table_name = quran_words_breakers)]
#[diesel(belongs_to(QuranWord, foreign_key = word_id))]
pub struct QuranWordBreaker {
    #[serde(skip_serializing)]
    id: i32,
    uuid: Uuid,

    #[serde(skip_serializing)]
    creator_user_id: i32,

    #[serde(skip_serializing)]
    pub word_id: i32,

    #[serde(skip_serializing)]
    owner_account_id: Option<i32>,

    pub name: String,

    #[serde(skip_serializing)]
    pub created_at: NaiveDateTime,
    #[serde(skip_serializing)]
    pub updated_at: NaiveDateTime,
}
