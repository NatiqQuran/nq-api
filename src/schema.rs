// @generated automatically by Diesel CLI.

diesel::table! {
    app_accounts (id) {
        id -> Int4,
        uuid -> Uuid,
        #[max_length = 30]
        username -> Varchar,
        account_type -> Text,
    }
}

diesel::table! {
    app_emails (id) {
        id -> Int4,
        account_id -> Int4,
        creator_user_id -> Int4,
        email -> Text,
        verified -> Bool,
        primary -> Bool,
        deleted -> Bool,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_employees (id) {
        id -> Int4,
        org_account_id -> Int4,
        creator_user_id -> Int4,
        employee_account_id -> Int4,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_error_logs (id) {
        id -> Int4,
        uuid -> Uuid,
        #[max_length = 256]
        error_name -> Varchar,
        status_code -> Int4,
        message -> Text,
        detail -> Nullable<Text>,
        account_id -> Nullable<Int4>,
        #[max_length = 64]
        request_token -> Nullable<Varchar>,
        request_user_agent -> Nullable<Text>,
        request_ipv4 -> Cidr,
        request_url -> Nullable<Text>,
        request_controller -> Nullable<Text>,
        request_action -> Nullable<Text>,
        request_id -> Nullable<Text>,
        request_body -> Nullable<Bytea>,
        request_body_content_type -> Nullable<Text>,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_organization_names (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        account_id -> Int4,
        #[max_length = 300]
        name -> Varchar,
        #[max_length = 8]
        language -> Varchar,
    }
}

diesel::table! {
    app_organizations (id) {
        id -> Int4,
        account_id -> Int4,
        creator_user_id -> Int4,
        owner_account_id -> Int4,
        profile_image -> Nullable<Text>,
        established_date -> Date,
        #[max_length = 11]
        national_id -> Varchar,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_permission_conditions (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        permission_id -> Int4,
        #[max_length = 450]
        name -> Varchar,
        #[max_length = 255]
        value -> Varchar,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_permissions (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        account_id -> Int4,
        #[max_length = 255]
        object -> Varchar,
        #[max_length = 255]
        action -> Varchar,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_phrase_translations (id) {
        id -> Int4,
        uuid -> Uuid,
        phrase_id -> Int4,
        text -> Text,
        #[max_length = 3]
        language -> Varchar,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_phrases (id) {
        id -> Int4,
        uuid -> Uuid,
        phrase -> Text,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_tokens (id) {
        id -> Int4,
        account_id -> Int4,
        #[max_length = 64]
        token_hash -> Varchar,
        terminated -> Bool,
        terminated_by_id -> Int4,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_user_names (id) {
        id -> Int4,
        account_id -> Int4,
        creator_user_id -> Int4,
        primary_name -> Bool,
        #[max_length = 100]
        first_name -> Varchar,
        #[max_length = 200]
        last_name -> Varchar,
        #[max_length = 4]
        language -> Varchar,
    }
}

diesel::table! {
    app_users (id) {
        id -> Int4,
        account_id -> Int4,
        birthday -> Nullable<Date>,
        profile_image -> Nullable<Text>,
        #[max_length = 4]
        language -> Nullable<Varchar>,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    app_verify_codes (id) {
        id -> Int4,
        code -> Int4,
        email -> Text,
        status -> Text,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    quran_ayahs (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        surah_id -> Int4,
        ayah_number -> Int4,
        #[max_length = 20]
        sajdah -> Nullable<Varchar>,
        is_bismillah -> Bool,
        bismillah_text -> Nullable<Text>,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    quran_ayahs_breakers (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        ayah_id -> Int4,
        owner_account_id -> Nullable<Int4>,
        #[max_length = 256]
        name -> Varchar,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    quran_mushafs (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        #[max_length = 200]
        short_name -> Nullable<Varchar>,
        #[max_length = 400]
        name -> Nullable<Varchar>,
        #[max_length = 300]
        source -> Nullable<Varchar>,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    quran_surahs (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        #[max_length = 50]
        name -> Varchar,
        #[max_length = 50]
        period -> Nullable<Varchar>,
        number -> Int4,
        mushaf_id -> Int4,
        name_pronunciation -> Nullable<Text>,
        name_translation_phrase -> Nullable<Text>,
        name_transliteration -> Nullable<Text>,
        search_terms -> Nullable<Array<Nullable<Text>>>,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    quran_translations (id) {
        id -> Int4,
        uuid -> Uuid,
        mushaf_id -> Int4,
        creator_user_id -> Int4,
        translator_account_id -> Int4,
        #[max_length = 5]
        language -> Varchar,
        release_date -> Nullable<Date>,
        #[max_length = 300]
        source -> Nullable<Varchar>,
        approved -> Bool,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    quran_translations_ayahs (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        translation_id -> Int4,
        ayah_id -> Int4,
        text -> Text,
        bismillah -> Nullable<Text>,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    quran_words (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        ayah_id -> Int4,
        word -> Text,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::table! {
    quran_words_breakers (id) {
        id -> Int4,
        uuid -> Uuid,
        creator_user_id -> Int4,
        word_id -> Int4,
        owner_account_id -> Nullable<Int4>,
        #[max_length = 256]
        name -> Varchar,
        created_at -> Timestamptz,
        updated_at -> Timestamptz,
    }
}

diesel::joinable!(app_emails -> app_accounts (account_id));
diesel::joinable!(app_emails -> app_users (creator_user_id));
diesel::joinable!(app_employees -> app_users (creator_user_id));
diesel::joinable!(app_organization_names -> app_accounts (account_id));
diesel::joinable!(app_organization_names -> app_users (creator_user_id));
diesel::joinable!(app_organizations -> app_accounts (account_id));
diesel::joinable!(app_organizations -> app_users (creator_user_id));
diesel::joinable!(app_permission_conditions -> app_permissions (permission_id));
diesel::joinable!(app_permission_conditions -> app_users (creator_user_id));
diesel::joinable!(app_permissions -> app_accounts (account_id));
diesel::joinable!(app_permissions -> app_users (creator_user_id));
diesel::joinable!(app_phrase_translations -> app_phrases (phrase_id));
diesel::joinable!(app_tokens -> app_accounts (account_id));
diesel::joinable!(app_user_names -> app_accounts (account_id));
diesel::joinable!(app_user_names -> app_users (creator_user_id));
diesel::joinable!(app_users -> app_accounts (account_id));
diesel::joinable!(quran_ayahs -> app_users (creator_user_id));
diesel::joinable!(quran_ayahs -> quran_surahs (surah_id));
diesel::joinable!(quran_ayahs_breakers -> app_accounts (owner_account_id));
diesel::joinable!(quran_ayahs_breakers -> app_users (creator_user_id));
diesel::joinable!(quran_ayahs_breakers -> quran_ayahs (ayah_id));
diesel::joinable!(quran_mushafs -> app_users (creator_user_id));
diesel::joinable!(quran_surahs -> app_users (creator_user_id));
diesel::joinable!(quran_surahs -> quran_mushafs (mushaf_id));
diesel::joinable!(quran_translations -> app_accounts (translator_account_id));
diesel::joinable!(quran_translations -> app_users (creator_user_id));
diesel::joinable!(quran_translations -> quran_mushafs (mushaf_id));
diesel::joinable!(quran_translations_ayahs -> app_users (creator_user_id));
diesel::joinable!(quran_translations_ayahs -> quran_ayahs (ayah_id));
diesel::joinable!(quran_translations_ayahs -> quran_translations (translation_id));
diesel::joinable!(quran_words -> app_users (creator_user_id));
diesel::joinable!(quran_words -> quran_ayahs (ayah_id));
diesel::joinable!(quran_words_breakers -> app_accounts (owner_account_id));
diesel::joinable!(quran_words_breakers -> app_users (creator_user_id));
diesel::joinable!(quran_words_breakers -> quran_words (word_id));

diesel::allow_tables_to_appear_in_same_query!(
    app_accounts,
    app_emails,
    app_employees,
    app_error_logs,
    app_organization_names,
    app_organizations,
    app_permission_conditions,
    app_permissions,
    app_phrase_translations,
    app_phrases,
    app_tokens,
    app_user_names,
    app_users,
    app_verify_codes,
    quran_ayahs,
    quran_ayahs_breakers,
    quran_mushafs,
    quran_surahs,
    quran_translations,
    quran_translations_ayahs,
    quran_words,
    quran_words_breakers,
);
