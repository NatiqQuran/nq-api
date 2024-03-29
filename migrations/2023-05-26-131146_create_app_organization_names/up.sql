CREATE TABLE app_organization_names (
    id serial NOT NULL,
    uuid uuid DEFAULT uuid_generate_v4 () NOT NULL,
    creator_user_id serial NOT NULL,
    account_id serial NOT NULL,
    name VARCHAR(300) NOT NULL,
    language VARCHAR(8) NOT NULL,
    CONSTRAINT fk_org_names_account_id FOREIGN KEY(account_id) REFERENCES app_accounts(id),
    CONSTRAINT org_name_fk_user_id_rel FOREIGN KEY(creator_user_id) REFERENCES app_users(id),
    CONSTRAINT org_names_id PRIMARY KEY (id)
);
