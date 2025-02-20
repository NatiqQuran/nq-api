CREATE TABLE quran_ayahs_breakers (
    id serial,
    uuid uuid DEFAULT uuid_generate_v4 () NOT NULL,
    creator_user_id serial NOT NULL,
    ayah_id serial NOT NULL,
    owner_account_id INT REFERENCES app_accounts (id),
    name VARCHAR(256) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ayah_break_id PRIMARY KEY (id),
    CONSTRAINT fk_quran_ayah_break_creator_user_id FOREIGN KEY (creator_user_id) REFERENCES app_users (id),
    CONSTRAINT fk_break_ayah FOREIGN KEY (ayah_id) REFERENCES quran_ayahs (id) on delete cascade
);
