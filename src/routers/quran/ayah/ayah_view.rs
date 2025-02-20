use super::{AyahWithContentSurah, SimpleWord};
use crate::error::RouterError;
use crate::models::{QuranAyah, QuranMushaf, QuranSurah, QuranWord};
use crate::{routers::quran::surah::SurahName, AyahWithContent, DbPool, Sajdah, SingleSurahMushaf};
use ::uuid::Uuid;
use actix_web::web;
use diesel::prelude::*;
use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct GetAyahQuery {
    lang_code: Option<String>,
}

/// Return's a single ayah
pub async fn ayah_view(
    path: web::Path<Uuid>,
    web::Query(query): web::Query<GetAyahQuery>,
    pool: web::Data<DbPool>,
) -> Result<web::Json<AyahWithContent>, RouterError> {
    use crate::schema::app_phrase_translations::dsl::{
        app_phrase_translations, language as p_t_lang, text as p_t_text,
    };
    use crate::schema::app_phrases::dsl::{app_phrases, phrase as p_phrase};
    use crate::schema::quran_ayahs::dsl::{quran_ayahs, uuid as ayah_uuid};
    use crate::schema::quran_mushafs::dsl::{id as mushaf_id, quran_mushafs};
    use crate::schema::quran_surahs::dsl::{id as surah_id, quran_surahs};
    use crate::schema::quran_words::dsl::{ayah_id, id as word_id, quran_words};

    let requested_ayah_uuid = path.into_inner();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // Get the single ayah from the database
        let quran_ayah: QuranAyah = quran_ayahs
            .filter(ayah_uuid.eq(requested_ayah_uuid))
            .get_result(&mut conn)?;

        // Get the surah
        let surah = quran_surahs
            .filter(surah_id.eq(quran_ayah.surah_id))
            .get_result::<QuranSurah>(&mut conn)?;

        // Get the mushaf
        let mushaf = quran_mushafs
            .filter(mushaf_id.eq(surah.id))
            .get_result::<QuranMushaf>(&mut conn)?;

        let translation = if let Some(ref phrase) = surah.name_translation_phrase {
            let mut p = app_phrases.left_join(app_phrase_translations).into_boxed();

            if let Some(ref l) = query.lang_code {
                p = p.filter(p_t_lang.eq(l));
            } else {
                p = p.filter(p_t_lang.eq("en"));
            }

            p.filter(p_phrase.eq(phrase))
                .select(p_t_text.nullable())
                .get_result(&mut conn)?
        } else {
            None
        };
        let words: Vec<QuranWord> = quran_words
            .filter(ayah_id.eq(quran_ayah.id))
            .order(word_id.asc())
            .get_results(&mut conn)?;

        let words_simple: Vec<SimpleWord> = words
            .into_iter()
            .map(|word| SimpleWord {
                word: word.word,
                uuid: word.uuid,
            })
            .collect();

        let text = words_simple
            .clone()
            .into_iter()
            .map(|word| word.word)
            .collect::<Vec<String>>()
            .join(" ");

        Ok(web::Json(AyahWithContent {
            surah: AyahWithContentSurah {
                uuid: surah.uuid,
                names: vec![SurahName {
                    arabic: surah.name,
                    translation,
                    translation_phrase: surah.name_translation_phrase,
                    pronunciation: surah.name_pronunciation,
                    transliteration: surah.name_transliteration,
                }],
            },
            mushaf: SingleSurahMushaf::from(mushaf),
            sajdah: Sajdah::from_option_string(quran_ayah.sajdah),
            ayah_number: quran_ayah.ayah_number,
            words: words_simple,
            text,
        }))
    })
    .await
    .unwrap()
}
