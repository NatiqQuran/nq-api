pub mod ayah_add;
pub mod ayah_delete;
pub mod ayah_edit;
pub mod ayah_list;
pub mod ayah_view;

use std::fmt::Display;

use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{
    filter::{Filters, Order},
    AyahBismillah, Format, SingleSurahMushaf, SurahName,
};

#[derive(Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum Sajdah {
    Mostahab,
    Vajib,
}

impl Display for Sajdah {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Mostahab => write!(f, "mostahab"),
            Self::Vajib => write!(f, "vajib"),
        }
    }
}

impl Sajdah {
    pub fn from_option_string(value: Option<String>) -> Option<Self> {
        let value = value?;

        match value.as_str() {
            "vajib" => Some(Self::Vajib),
            "mostahab" => Some(Self::Mostahab),

            _ => None,
        }
    }
}

#[derive(Clone, Serialize, Deserialize)]
pub struct SimpleWord {
    uuid: Uuid,
    word: String,
}

#[derive(Serialize)]
pub struct AyahWithContentSurah {
    uuid: Uuid,
    names: Vec<SurahName>,
}

#[derive(Serialize)]
pub struct AyahWithContent {
    mushaf: SingleSurahMushaf,
    surah: AyahWithContentSurah,
    ayah_number: i32,
    sajdah: Option<Sajdah>,
    text: String,
    words: Vec<SimpleWord>,
}

#[derive(Serialize, Deserialize)]
pub struct SimpleAyah {
    pub ayah_number: i32,
    pub sajdah: Option<Sajdah>,
    pub bismillah: Option<AyahBismillah>,
}

#[derive(Deserialize, Clone)]
pub struct AyahListQuery {
    mushaf: String,
    format: Option<Format>,

    sort: Option<String>,
    order: Option<Order>,

    from: Option<u64>,
    to: Option<u64>,
}

impl Filters for AyahListQuery {
    fn sort(&self) -> Option<String> {
        self.sort.clone()
    }

    fn order(&self) -> Option<Order> {
        self.order.clone()
    }

    fn from(&self) -> Option<u64> {
        self.from
    }

    fn to(&self) -> Option<u64> {
        self.to
    }
}
