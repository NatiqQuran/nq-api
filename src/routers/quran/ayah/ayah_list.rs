use std::collections::HashMap;

use crate::error::{RouterError, RouterErrorDetailBuilder};
use crate::filter::Filter;
use crate::models::{QuranAyah, QuranAyahBreaker, QuranWord, QuranWordBreaker};
use crate::routers::multip;
use crate::routers::quran::word::WordBreaker;
use crate::{
    routers::quran::surah::{AyahTy, AyahWord, Format, SimpleAyah},
    DbPool,
};
use crate::{AyahBismillah, Breaker};
use actix_web::{web, HttpRequest};
use diesel::prelude::*;

use super::AyahListQuery;

/// Returns the list of ayahs
pub async fn ayah_list(
    pool: web::Data<DbPool>,
    web::Query(query): web::Query<AyahListQuery>,
    req: HttpRequest,
) -> Result<web::Json<Vec<AyahTy>>, RouterError> {
    use crate::schema::quran_ayahs::dsl::ayah_number;
    use crate::schema::quran_ayahs_breakers::dsl::quran_ayahs_breakers;
    use crate::schema::quran_mushafs::dsl::{quran_mushafs, short_name as mushaf_short_name};
    use crate::schema::quran_surahs::dsl::{number as quran_surah_number, quran_surahs};
    use crate::schema::quran_words::dsl::quran_words;
    use crate::schema::quran_words_breakers::dsl::quran_words_breakers;

    let pool = pool.into_inner();

    let error_detail = RouterErrorDetailBuilder::from_http_request(&req).build();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        // [{ayah_id, name}...]
        // Also need to count name
        let breakers: Vec<QuranAyahBreaker> = quran_ayahs_breakers.get_results(&mut conn)?;
        let mut breakers = breakers.into_iter();

        let mut breakers_count: HashMap<String, u32> = HashMap::new();
        let mut map = HashMap::<i32, Vec<Breaker>>::new();

        while let Some(breaker) = breakers.next() {
            breakers_count
                .entry(breaker.name)
                .and_modify(|v| *v += 1)
                .or_insert(1);

            let val = breakers_count
                .clone()
                .into_iter()
                .map(|(k, v)| Breaker { name: k, number: v })
                .collect::<Vec<Breaker>>();

            map.entry(breaker.ayah_id).insert_entry(val);
        }

        // TODO: this gets every word's breaker. (not efficient)
        let words_breakers = if matches!(query.format, Some(Format::Word)) {
            let breakers: Vec<QuranWordBreaker> = quran_words_breakers.get_results(&mut conn)?;
            let mut breakers = breakers.into_iter();
            // (i32)
            let mut collected_breakers: HashMap<i32, Vec<WordBreaker>> = HashMap::new();

            while let Some(breaker) = breakers.next() {
                collected_breakers
                    .entry(breaker.word_id)
                    .and_modify(|v| {
                        v.push(WordBreaker {
                            name: breaker.name.clone(),
                        })
                    })
                    .or_insert(vec![WordBreaker { name: breaker.name }]);
            }

            Some(collected_breakers)
        } else {
            None
        };

        let filtered_ayahs = match QuranAyah::filter(Box::from(query.clone())) {
            Ok(filtered) => filtered,
            Err(err) => return Err(err.log_to_db(pool, error_detail)),
        };

        let ayahs_words = filtered_ayahs
            .left_outer_join(quran_surahs.left_outer_join(quran_mushafs))
            // TODO: currently we dont use quran_words_breakers join
            .inner_join(quran_words.left_join(quran_words_breakers))
            .filter(mushaf_short_name.eq(query.mushaf))
            .order((quran_surah_number.asc(), ayah_number.asc()))
            .select((QuranAyah::as_select(), QuranWord::as_select()))
            .get_results::<(QuranAyah, QuranWord)>(&mut conn)?;

        let ayahs_words = ayahs_words
            .into_iter()
            .map(|(ayah, word)| {
                (
                    SimpleAyah {
                        id: ayah.id as u32,
                        uuid: ayah.uuid,
                        bismillah: AyahBismillah::from_ayah_fields(
                            ayah.is_bismillah,
                            ayah.bismillah_text,
                        ),
                        breakers: map.get(&ayah.id).clone().cloned(),
                        number: ayah.ayah_number as u32,
                        sajdah: ayah.sajdah,
                    },
                    word,
                )
            })
            .collect::<Vec<(SimpleAyah, QuranWord)>>();

        let ayahs_as_map = multip(ayahs_words, |a| a);
        let final_ayahs = ayahs_as_map
            .into_iter()
            .map(|(ayah, words)| match query.format {
                Some(Format::Text) | None => AyahTy::Text(crate::AyahWithText {
                    ayah,
                    text: words
                        .into_iter()
                        .map(|w| w.word)
                        .collect::<Vec<String>>()
                        .join(" "),
                }),
                Some(Format::Word) => AyahTy::Words(crate::AyahWithWords {
                    ayah: ayah.clone(),
                    words: words
                        .into_iter()
                        .map(|w| AyahWord {
                            // TODO: Very expensive operation. remove .clone()
                            breakers: words_breakers.clone().unwrap().get(&w.id).clone().cloned(),
                            word: w.word,
                        })
                        .collect(),
                }),
            })
            .collect::<Vec<AyahTy>>();

        Ok(web::Json(final_ayahs))
    })
    .await
    .unwrap()
}
