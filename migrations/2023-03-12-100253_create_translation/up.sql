CREATE TABLE quran_translations (
    id serial NOT NULL,
    uuid uuid DEFAULT uuid_generate_v4 () NOT NULL,
    mushaf_id serial NOT NULL,
    creator_user_id serial NOT NULL,
    translator_account_id serial NOT NULL,
    language VARCHAR(5) NOT NULL,
    release_date DATE,
    source VARCHAR(300),
    approved BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT translation_fk_user_id_rel FOREIGN KEY(creator_user_id) REFERENCES app_users(id),
    CONSTRAINT translation_mushaf_fk_id_rel FOREIGN KEY(mushaf_id) REFERENCES quran_mushafs(id) on delete cascade,
    CONSTRAINT translation_id PRIMARY KEY (id),
    CONSTRAINT fk_translator_account_rel FOREIGN KEY(translator_account_id) REFERENCES app_accounts(id)
);
