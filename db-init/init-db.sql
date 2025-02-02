CREATE TABLE users_user (
    id bigserial PRIMARY KEY,
    username text NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,  
    email text,
    phone bigint,
    logged_in boolean NOT NULL DEFAULT false,
    admin boolean NOT NULL DEFAULT false
);
CREATE UNIQUE INDEX users_user_username_key ON users_user(username);

CREATE TABLE teams_team (
    id bigserial PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE,
    equipment_admin boolean NOT NULL DEFAULT false
);

CREATE TABLE equipments_site (
    id bigserial PRIMARY KEY,
    name varchar(200) NOT NULL,
    additional_info text
);

CREATE TABLE equipments_equipmenttype (
    id bigserial PRIMARY KEY,
    name varchar(200) NOT NULL
);

CREATE TABLE tickets_category (
    id bigserial PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE
);

CREATE TABLE tickets_tickettype (
    id bigserial PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE tickets_ticketstatustype (
    id bigserial PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE equipments_equipment (
    id bigserial PRIMARY KEY,
    name varchar(200) NOT NULL,
    site_id bigint NOT NULL,
    type_id bigint NOT NULL,
    last_change_ticket bigint,
    first_level_support_team_id bigint NOT NULL,
    second_level_support_team_id bigint NOT NULL,
    additional_info text,
    CONSTRAINT fk_equip_site FOREIGN KEY (site_id)
        REFERENCES equipments_site (id) ON DELETE CASCADE,
    CONSTRAINT fk_equip_type FOREIGN KEY (type_id)
        REFERENCES equipments_equipmenttype (id) ON DELETE CASCADE,
    CONSTRAINT fk_equip_first_team FOREIGN KEY (first_level_support_team_id)
        REFERENCES teams_team (id) ON DELETE CASCADE,
    CONSTRAINT fk_equip_second_team FOREIGN KEY (second_level_support_team_id)
        REFERENCES teams_team (id) ON DELETE CASCADE
);

CREATE TABLE tickets_ticket (
    id bigserial PRIMARY KEY,
    type_id bigint NOT NULL,
    creator_id bigint NOT NULL,
    category_id bigint NOT NULL,
    owner_team_id bigint NOT NULL,
    status_id bigint NOT NULL,
    issue_started timestamptz NOT NULL,
    issue_resolved timestamptz,
    CONSTRAINT fk_ticket_type FOREIGN KEY (type_id)
        REFERENCES tickets_tickettype (id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_creator FOREIGN KEY (creator_id)
        REFERENCES users_user (id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_category FOREIGN KEY (category_id)
        REFERENCES tickets_category (id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_owner_team FOREIGN KEY (owner_team_id)
        REFERENCES teams_team (id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_status FOREIGN KEY (status_id)
        REFERENCES tickets_ticketstatustype (id) ON DELETE CASCADE
);

CREATE TABLE tickets_commenttype (
    id bigserial PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE tickets_comment (
    id bigserial PRIMARY KEY,
    username_id bigint NOT NULL,
    ticket_id bigint NOT NULL,
    comment_text text NOT NULL,
    comment_type_id bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_comment_user FOREIGN KEY (username_id)
        REFERENCES users_user (id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_ticket FOREIGN KEY (ticket_id)
        REFERENCES tickets_ticket (id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_type FOREIGN KEY (comment_type_id)
        REFERENCES tickets_commenttype (id) ON DELETE CASCADE
);

CREATE TABLE tickets_ticketacknowledgmentstatus (
    id bigserial PRIMARY KEY,
    name varchar(50) NOT NULL UNIQUE
);

CREATE TABLE tickets_ticketrequestedteam (
    id bigserial PRIMARY KEY,
    ticket_id bigint NOT NULL,
    team_id bigint NOT NULL,
    status_id bigint NOT NULL,
    CONSTRAINT fk_trt_ticket FOREIGN KEY (ticket_id)
        REFERENCES tickets_ticket (id) ON DELETE CASCADE,
    CONSTRAINT fk_trt_team FOREIGN KEY (team_id)
        REFERENCES teams_team (id) ON DELETE CASCADE,
    CONSTRAINT fk_trt_status FOREIGN KEY (status_id)
        REFERENCES tickets_ticketacknowledgmentstatus (id) ON DELETE CASCADE
);

CREATE TABLE tickets_ticketsaffectedequipment (
    id bigserial PRIMARY KEY,
    ticket_id bigint NOT NULL,
    equipment_id bigint NOT NULL,
    CONSTRAINT fk_tickets_affectedequipment_ticket FOREIGN KEY (ticket_id)
        REFERENCES tickets_ticket (id) ON DELETE CASCADE,
    CONSTRAINT fk_tickets_affectedequipment_equipment FOREIGN KEY (equipment_id)
        REFERENCES equipments_equipment (id) ON DELETE CASCADE
);

CREATE TABLE teams_userteam (
    id bigserial PRIMARY KEY,
    team_id bigint NOT NULL,
    user_id bigint NOT NULL,
    teamadmin boolean NOT NULL DEFAULT false,
    CONSTRAINT unique_team_user UNIQUE (team_id, user_id),
    CONSTRAINT fk_userteam_team FOREIGN KEY (team_id)
        REFERENCES teams_team (id) ON DELETE CASCADE,
    CONSTRAINT fk_userteam_user FOREIGN KEY (user_id)
        REFERENCES users_user (id) ON DELETE CASCADE
);


CREATE ROLE application WITH LOGIN PASSWORD 'secure_password';

-- Grant database connection access
GRANT CONNECT ON DATABASE itsm TO application;

-- Grant usage on schema (but NOT all public schema objects)
GRANT USAGE ON SCHEMA public TO application;

-- Grant permissions only to the specified tables
GRANT SELECT, INSERT, UPDATE, DELETE ON tickets_category, tickets_tickettype, tickets_ticketstatustype, tickets_ticket,
                                       tickets_commenttype, tickets_comment, tickets_ticketacknowledgmentstatus,
                                       tickets_ticketrequestedteam, tickets_ticketsaffectedequipment, users_user,
                                       teams_team, teams_userteam, equipments_site, equipments_equipmenttype,
                                       equipments_equipment
TO application;

-- Grant permissions on sequences (needed for ID auto-increments)
GRANT USAGE, SELECT ON SEQUENCE tickets_category_id_seq, tickets_tickettype_id_seq, tickets_ticketstatustype_id_seq,
                                  tickets_ticket_id_seq, tickets_commenttype_id_seq, tickets_comment_id_seq,
                                  tickets_ticketacknowledgmentstatus_id_seq, tickets_ticketrequestedteam_id_seq,
                                  tickets_ticketsaffectedequipment_id_seq, users_user_id_seq, teams_team_id_seq,
                                  teams_userteam_id_seq, equipments_site_id_seq, equipments_equipmenttype_id_seq,
                                  equipments_equipment_id_seq
TO application;




-- Ensure new tables created in the future do not automatically inherit privileges 
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM application;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM application;

