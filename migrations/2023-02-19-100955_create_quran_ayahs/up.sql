CREATE TABLE quran_ayahs (
    id serial NOT NULL,
    uuid uuid DEFAULT uuid_generate_v4 () NOT NULL,
    creator_user_id serial NOT NULL,
    surah_id serial NOT NULL,
    ayah_number serial NOT NULL,
    sajdah VARCHAR(20),
    is_bismillah BOOLEAN NOT NULL,
    bismillah_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT quran_ayahs_id PRIMARY KEY (id),
    CONSTRAINT ayah_fk_user_id_rel FOREIGN KEY(creator_user_id) REFERENCES app_users(id),
    CONSTRAINT fk_surah_id FOREIGN KEY(surah_id) REFERENCES quran_surahs(id)
        on delete cascade
);
