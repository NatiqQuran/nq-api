use crate::{datetime::parse_date_time_with_format, test::Test};
use chrono::NaiveDate;
use serde::{Deserialize, Serialize};
use validator::Validate;

#[derive(Deserialize, Validate, Serialize)]
pub struct NewOrgInfo {
    pub username: String,
    pub name: String,
    pub profile_image: Option<String>,

    #[serde(deserialize_with = "parse_date_time_with_format")]
    pub established_date: NaiveDate,

    #[validate(length(equal = 11))]
    pub national_id: String,
}

impl Test for NewOrgInfo {
    fn test() -> Self {
        Self {
            username: String::from("NatiqQuran"),
            name: String::from("Natiq Quran"),
            profile_image: None,
            established_date: NaiveDate::from_ymd(2021, 11, 21),
            national_id: String::from("12345678911"),
        }
    }
}
