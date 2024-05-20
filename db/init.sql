CREATE USER repl_user REPLICATION LOGIN PASSWORD 'Qq12345';

CREATE TABLE public.emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL
);

CREATE TABLE public.phones (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(50) NOT NULL
);

INSERT INTO emails (email) VALUES ('email@test.test'), ('r.klimov@innopolis.university');
INSERT INTO phones (phone) VALUES ('+7(911) 123-45-67'), ('89111234567');
select pg_create_physical_replication_slot('replication_slot');