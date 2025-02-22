use crate::error::RouterError;
use crate::models::QuranWord;
use crate::DbPool;
use ::uuid::Uuid;
use actix_web::web;
use diesel::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub struct WordViewResponse {
    word: String,
}

/// Return's a single word
pub async fn word_view(
    path: web::Path<Uuid>,
    pool: web::Data<DbPool>,
) -> Result<web::Json<WordViewResponse>, RouterError> {
    use crate::schema::quran_words::dsl::{quran_words, uuid as word_uuid};

    let requested_word_uuid = path.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // Get the single word from the database
        let quran_word: QuranWord = quran_words
            .filter(word_uuid.eq(requested_word_uuid))
            .get_result(&mut conn)?;

        Ok(web::Json(WordViewResponse {
            word: quran_word.word,
        }))
    })
    .await
    .unwrap()
}
