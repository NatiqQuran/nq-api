use crate::error::{RouterError, RouterErrorDetailBuilder};
use crate::filter::Filter;
use crate::models::QuranAyah;
use crate::routers::multip;
use crate::{
    routers::quran::surah::{AyahTy, Format, SimpleAyah},
    DbPool,
};
use actix_web::{web, HttpRequest};
use diesel::prelude::*;

use super::AyahListQuery;

/// Returns the list of ayahs
pub async fn ayah_list(
    pool: web::Data<DbPool>,
    web::Query(query): web::Query<AyahListQuery>,
    req: HttpRequest,
) -> Result<web::Json<Vec<AyahTy>>, RouterError> {
    use crate::schema::quran_mushafs::dsl::{quran_mushafs, short_name as mushaf_short_name};
    use crate::schema::quran_surahs::dsl::quran_surahs;
    use crate::schema::quran_words::dsl::{quran_words, word as q_word};

    let pool = pool.into_inner();

    let error_detail = RouterErrorDetailBuilder::from_http_request(&req).build();

    web::block(move || {
        let mut conn = pool.get().unwrap();

        let filtered_ayahs = match QuranAyah::filter(Box::from(query.clone())) {
            Ok(filtered) => filtered,
            Err(err) => return Err(err.log_to_db(pool, error_detail)),
        };

        let ayahs = filtered_ayahs
            .left_outer_join(quran_surahs.left_outer_join(quran_mushafs))
            .inner_join(quran_words)
            .filter(mushaf_short_name.eq(query.mushaf))
            .select((QuranAyah::as_select(), q_word))
            .get_results::<(QuranAyah, String)>(&mut conn)?;

        let ayahs_as_map = multip(ayahs, |a| SimpleAyah {
            number: a.ayah_number,
            uuid: a.uuid,
            sajdah: a.sajdah,
        });

        let final_ayahs = ayahs_as_map
            .into_iter()
            .map(|(ayah, words)| match query.format {
                Some(Format::Text) | None => AyahTy::Text(crate::AyahWithText {
                    ayah,
                    text: words
                        .into_iter()
                        .map(|word| word)
                        .collect::<Vec<String>>()
                        .join(" "),
                }),
                Some(Format::Word) => AyahTy::Words(crate::AyahWithWords {
                    ayah,
                    words: words.into_iter().map(|word| word).collect(),
                }),
            })
            .collect::<Vec<AyahTy>>();

        Ok(web::Json(final_ayahs))
    })
    .await
    .unwrap()
}
