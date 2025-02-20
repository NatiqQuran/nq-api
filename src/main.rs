use crate::error::PreDefinedResponseError;
use actix_cors::Cors;
use actix_web::web::PathConfig;
use actix_web::{middleware, web, App, HttpServer};
use authz::AuthZController;
use diesel_migrations::{embed_migrations, EmbeddedMigrations, MigrationHarness};

use auth_n::middleware::TokenAuth;
use auth_z::middleware::AuthZ;
use diesel::pg::PgConnection;
use diesel::r2d2::{ConnectionManager, Pool};
use dotenvy::dotenv;
use email::EmailManager;
use error::{path_error_handler, PreDefinedResponseErrors};
use lettre::transport::smtp::authentication::Credentials;
use log::LevelFilter;
use log4rs::append::file::FileAppender;
use log4rs::config::{Appender, Root};
use log4rs::encode::pattern::PatternEncoder;
use log4rs::Config;
use std::collections::HashMap;
use std::error::Error;
use std::io::ErrorKind;
use std::sync::OnceLock;
use std::{env, io};
use token_checker::UserIdFromToken;

mod authz;
mod datetime;
mod email;
mod error;
mod filter;
pub mod models;
mod models_filter;
mod routers;
mod schema;
mod select_model;
mod token_checker;
mod validate;

mod difference;
mod macros;

use routers::account::logout;
use routers::account::send_code;
use routers::account::verify;
use routers::error::errors_list;
use routers::organization::{add, delete, edit, list, name, view};
use routers::permission::{
    add_permission, delete_permission, edit_permission, permissions_list, view_permission,
};
use routers::phrase::{add_phrase, delete_phrase, edit_phrase, phrase_list, view_phrase};
use routers::profile::{profile_edit, profile_view};
use routers::quran::{ayah::*, mushaf::*, surah::*, word::*};
use routers::translation::*;
use routers::user::{add_user, delete_user, edit_user, users_list, view_user};

pub type DbPool = Pool<ConnectionManager<PgConnection>>;

pub const MIGRATIONS: EmbeddedMigrations = embed_migrations!("./migrations");

/// Predefined NQ-api errors that is loadeded from (static) file has life time of static.
pub static FIXED_ERROR_RESPONSES: OnceLock<PreDefinedResponseErrors> = OnceLock::new();
pub const FIXED_ERROR_JSON: &str = include_str!("../error_codes.json");

fn run_migrations(
    connection: &mut PgConnection,
) -> Result<(), Box<dyn Error + Send + Sync + 'static>> {
    // This will run the necessary migrations.
    //
    // See the documentation for `MigrationHarness` for
    // all available methods.
    connection.run_pending_migrations(MIGRATIONS)?;

    Ok(())
}

pub fn create_emailer() -> EmailManager {
    let host = env::var("SMTP_HOST").expect("SMTP_HOST must be set");
    let port = env::var("SMTP_PORT").expect("SMTP_PORT must be set");
    let from = env::var("SMTP_FROM").expect("SMTP_FROM must be set");
    let username = env::var("SMTP_USERNAME").expect("SMTP_USERNAME must be set");
    let password = env::var("SMTP_PASSWORD").expect("SMTP_PASSWORD must be set");

    let credentials = Credentials::new(username, password);

    EmailManager::new(&host, port.parse().unwrap(), credentials, from)
        .expect("Cant create EmailManager")
}

pub fn establish_database_connection() -> ConnectionManager<PgConnection> {
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");

    ConnectionManager::<PgConnection>::new(database_url)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok();

    let file_log = FileAppender::builder()
        .encoder(Box::new(PatternEncoder::new("{d} - {m}{n}")))
        .build("$ENV{LOG_FILE_PATH}")
        .unwrap();

    let log_config = Config::builder()
        .appender(Appender::builder().build("logfile", Box::new(file_log)))
        .build(
            Root::builder()
                .appender("logfile")
                .build(LevelFilter::Error),
        )
        .unwrap();

    // Don't need to change configuration on runtime for now
    let _handle = log4rs::init_config(log_config).unwrap();

    let Ok(json) =
        serde_json::from_str::<HashMap<String, PreDefinedResponseError>>(FIXED_ERROR_JSON)
    else {
        return Err(io::Error::new(
            ErrorKind::Other,
            "Failed to parse fixed_error_responses json!",
        ));
    };

    let Ok(()) = FIXED_ERROR_RESPONSES.set(PreDefinedResponseErrors { errors: json }) else {
        return Err(io::Error::new(
            ErrorKind::Other,
            "Could't set to static FIXED_ERROR_RESPONSES",
        ));
    };

    let pg_manager = establish_database_connection();

    let pool = Pool::builder()
        .build(pg_manager)
        .expect("Failed to create pool.");

    run_migrations(&mut pool.get().unwrap()).unwrap();

    let mailer = create_emailer();

    let user_id_from_token = UserIdFromToken::new(pool.clone());

    let auth_z_controller = AuthZController::new(pool.clone());

    HttpServer::new(move || {
        // Set All to the cors
        let cors = Cors::permissive();

        App::new()
            .wrap(cors)
            .wrap(middleware::DefaultHeaders::new().add(("Cache-Control", "no-cache")))
            .app_data(PathConfig::default().error_handler(path_error_handler))
            .app_data(web::Data::new(pool.clone()))
            .app_data(web::Data::new(mailer.clone()))
            .service(
                web::scope("/account")
                    .route("/sendCode", web::post().to(send_code::send_code))
                    .route("/verify", web::post().to(verify::verify))
                    .service(
                        web::resource("/logout")
                            .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                            .route(web::get().to(logout::logout)),
                    ),
            )
            .service(
                web::scope("/surah")
                    .route("", web::get().to(surah_list::surah_list))
                    .route("/{surah_uuid}", web::get().to(surah_view::surah_view))
                    .service(
                        web::resource("")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                            .route(web::post().to(surah_add::surah_add)),
                    )
                    .service(
                        web::resource("/{surah_uuid}")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            // These routers don't need user token.
                            .wrap(TokenAuth::new(user_id_from_token.clone(), false))
                            .route(web::post().to(surah_edit::surah_edit))
                            .route(web::delete().to(surah_delete::surah_delete)),
                    ),
            )
            .service(
                web::scope("/translation")
                    .route("", web::get().to(translation_list::translation_list))
                    .route(
                        "/{translation_uuid}",
                        web::get().to(translation_view::translation_view),
                    )
                    .service(
                        web::resource("")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                            .route(web::post().to(translation_add::translation_add)),
                    )
                    .service(
                        web::resource("/{translation_uuid}")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            .wrap(TokenAuth::new(user_id_from_token.clone(), false))
                            .route(web::post().to(translation_edit::translation_edit))
                            .route(web::delete().to(translation_delete::translation_delete)),
                    )
                    .service(
                        web::scope("/text")
                            .route(
                                "/{translation_uuid}",
                                web::get().to(translation_ayah_view::translation_ayah_view),
                            )
                            .service(
                                web::resource("/{translation_uuid}")
                                    .wrap(AuthZ::new(auth_z_controller.clone()))
                                    .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                                    .route(
                                        web::post()
                                            .to(translation_ayah_modify::translation_ayah_modify),
                                    )
                                    .route(
                                        web::delete()
                                            .to(translation_ayah_delete::translation_ayah_delete),
                                    ),
                            ),
                    ),
            )
            .service(
                web::scope("/ayah")
                    .route("", web::get().to(ayah_list::ayah_list))
                    .route("/{ayah_uuid}", web::get().to(ayah_view::ayah_view))
                    .service(
                        web::resource("")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                            .route(web::post().to(ayah_add::ayah_add)),
                    )
                    .service(
                        web::resource("/{ayah_uuid}")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                            .route(web::post().to(ayah_edit::ayah_edit))
                            .route(web::delete().to(ayah_delete::ayah_delete)),
                    ),
            )
            .service(
                web::scope("/word")
                    .route("/{word_uuid}", web::get().to(word_view::word_view))
                    .service(
                        web::resource("")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                            .route(web::post().to(word_add::word_add)),
                    )
                    .service(
                        web::resource("/{word_uuid}")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            .wrap(TokenAuth::new(user_id_from_token.clone(), false))
                            .route(web::post().to(word_edit::word_edit))
                            .route(web::delete().to(word_delete::word_delete)),
                    ),
            )
            .service(
                web::scope("/mushaf")
                    .route("", web::get().to(mushaf_list::mushaf_list))
                    .route("/{mushaf_uuid}", web::get().to(mushaf_view::mushaf_view))
                    .service(
                        web::resource("")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                            .route(web::post().to(mushaf_add::mushaf_add)),
                    )
                    .service(
                        web::resource("/{mushaf_uuid}")
                            .wrap(AuthZ::new(auth_z_controller.clone()))
                            .wrap(TokenAuth::new(user_id_from_token.clone(), false))
                            .route(web::post().to(mushaf_edit::mushaf_edit))
                            .route(web::delete().to(mushaf_delete::mushaf_delete)),
                    ),
            )
            .service(
                web::scope("/user")
                    .wrap(AuthZ::new(auth_z_controller.clone()))
                    .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                    .route("", web::get().to(users_list::users_list))
                    .route("", web::post().to(add_user::add_user))
                    .route("/{uuid}", web::get().to(view_user::view_user))
                    .route("/{uuid}", web::post().to(edit_user::edit_user))
                    .route("/{uuid}", web::delete().to(delete_user::delete_user)),
            )
            .service(
                web::scope("/profile")
                    .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                    .route("", web::get().to(profile_view::profile_view))
                    .route("", web::post().to(profile_edit::profile_edit)),
            )
            .service(
                web::scope("/organization")
                    .wrap(AuthZ::new(auth_z_controller.clone()))
                    .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                    .route("/name", web::post().to(name::add_name))
                    .route("/name/{uuid}", web::get().to(name::names))
                    .route("/name/{uuid}", web::post().to(name::edit_name))
                    .route("/name/{uuid}", web::delete().to(name::delete_name))
                    .route("", web::get().to(list::get_list_of_organizations))
                    .route("", web::post().to(add::add))
                    .route("/{account_uuid}", web::get().to(view::view))
                    .route("/{account_uuid}", web::post().to(edit::edit_organization))
                    .route(
                        "/{account_uuid}",
                        web::delete().to(delete::delete_organization),
                    ),
            )
            .service(
                web::scope("/permission")
                    .wrap(AuthZ::new(auth_z_controller.clone()))
                    .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                    .route("", web::get().to(permissions_list::get_list_of_permissions))
                    .route("", web::post().to(add_permission::add_permission))
                    .route(
                        "/{permission_uuid}",
                        web::get().to(view_permission::get_permission),
                    )
                    .route(
                        "/{permission_uuid}",
                        web::post().to(edit_permission::edit_permission),
                    )
                    .route(
                        "/{permission_uuid}",
                        web::delete().to(delete_permission::delete_permission),
                    ),
            )
            .service(
                web::scope("/error")
                    .wrap(AuthZ::new(auth_z_controller.clone()))
                    .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                    .route("", web::get().to(errors_list)),
            )
            .service(
                web::scope("/phrase")
                    .wrap(AuthZ::new(auth_z_controller.clone()))
                    .wrap(TokenAuth::new(user_id_from_token.clone(), true))
                    .route("", web::get().to(phrase_list::list_phrase))
                    .route("", web::post().to(add_phrase::add_phrase))
                    .route("/{language}", web::get().to(view_phrase::view_phrase))
                    .route("/{language}", web::post().to(edit_phrase::edit_phrase))
                    .route(
                        "/{language}",
                        web::delete().to(delete_phrase::delete_phrase),
                    ),
            )
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}
