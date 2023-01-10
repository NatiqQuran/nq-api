use actix_cors::Cors;
use actix_web::{web, App, HttpServer};
use diesel_migrations::{embed_migrations, EmbeddedMigrations, MigrationHarness};

use auth::token::TokenAuth;
use diesel::pg::PgConnection;
use diesel::r2d2::{ConnectionManager, Pool};
use dotenvy::dotenv;
use email::EmailManager;
use lettre::transport::smtp::authentication::Credentials;
use std::env;
use std::error::Error;
use token_checker::UserIdFromToken;

mod datetime;
mod email;
mod models;
mod routers;
mod schema;
mod test;
mod token_checker;
mod validate;

use routers::account::logout;
use routers::account::send_code;
use routers::account::verify;
use routers::organization::add;
use routers::organization::edit;
use routers::organization::list;
use routers::organization::view;
use routers::profile::profile;
use routers::quran::quran;

type DbPool = Pool<ConnectionManager<PgConnection>>;

pub const MIGRATIONS: EmbeddedMigrations = embed_migrations!("./migrations");

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
    dotenv().ok();

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
    dotenv().ok();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");

    ConnectionManager::<PgConnection>::new(database_url)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let pg_manager = establish_database_connection();

    let pool = Pool::builder()
        .build(pg_manager)
        .expect("Failed to create pool.");

    run_migrations(&mut pool.get().unwrap()).unwrap();

    let mailer = create_emailer();

    let user_id_from_token = UserIdFromToken::new(pool.clone());

    HttpServer::new(move || {
        // Set All to the cors
        let cors = Cors::permissive();

        App::new()
            .wrap(cors)
            .app_data(web::Data::new(pool.clone()))
            .app_data(web::Data::new(mailer.clone()))
            .service(
                web::scope("/account")
                    .route("/sendCode", web::post().to(send_code::send_code))
                    .route("/verify", web::post().to(verify::verify))
                    .service(
                        web::resource("/logout")
                            .wrap(TokenAuth::new(user_id_from_token.clone()))
                            .route(web::get().to(logout::logout)),
                    ),
            )
            .service(web::resource("/quran").route(web::get().to(quran::quran)))
            .service(
                web::resource("/profile")
                    .wrap(TokenAuth::new(user_id_from_token.clone()))
                    .route(web::get().to(profile::view_profile)),
            )
            .service(
                web::scope("/organizations")
                    .wrap(TokenAuth::new(user_id_from_token.clone()))
                    .route("", web::get().to(list::get_list_of_organizations))
                    .route("", web::post().to(add::add))
                    .route("/{org_id}", web::get().to(view::view))
                    .route("/{org_id}", web::post().to(edit::edit_organization)),
            )
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}
