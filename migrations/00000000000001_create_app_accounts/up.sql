CREATE TABLE app_accounts (
    id serial PRIMARY KEY,
    uuid uuid DEFAULT uuid_generate_v4 () NOT NULL,
    username VARCHAR(30) NOT NULL,
    account_type TEXT NOT NULL,
    UNIQUE (username)
);
