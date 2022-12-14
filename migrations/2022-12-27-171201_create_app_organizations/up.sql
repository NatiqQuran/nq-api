-- Your SQL goes here

CREATE TABLE app_organizations(
    id serial NOT NULL,
    account_id serial NOT NULL,
    "name" VARCHAR(200) NOT NULL,
    profile_image TEXT,
    established_date DATE NOT NULL,
    national_id VARCHAR(11) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT app_organizations_id PRIMARY KEY (id),
    UNIQUE(account_id)
);
