pub mod word_add;
pub mod word_delete;
pub mod word_edit;
pub mod word_view;

use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct SimpleWord {
    pub word: String,
}

#[derive(Deserialize, Serialize, Debug, Clone)]
pub struct WordBreaker {
    pub name: String,
}
