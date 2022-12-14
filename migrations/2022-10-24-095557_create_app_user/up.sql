-- Your SQL goes here

CREATE TABLE app_users (
    id serial NOT NULL,
    account_id serial NOT NULL,
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    birthday TIMESTAMPTZ,
    profile_image TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT app_users_id PRIMARY KEY (id),
    UNIQUE(account_id)
);