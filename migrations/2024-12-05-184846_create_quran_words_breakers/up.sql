CREATE TABLE quran_words_breakers (
    id serial NOT NULL,
    uuid uuid DEFAULT uuid_generate_v4 () NOT NULL,
    creator_user_id serial NOT NULL,
    word_id serial NOT NULL,
    owner_account_id INT,
    name VARCHAR(256) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT word_break_id PRIMARY KEY (id),
    CONSTRAINT fk_quran_word_break_creator_user_id FOREIGN KEY (creator_user_id) REFERENCES app_users (id),
    CONSTRAINT fk_break_word FOREIGN KEY (word_id) REFERENCES quran_words (id) on delete cascade,
    CONSTRAINT fk_word_break_owner_account_rel FOREIGN KEY (owner_account_id) REFERENCES app_accounts (id)
);
