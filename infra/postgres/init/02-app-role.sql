-- Runtime role for Task/Team services, which enforce tenant isolation with RLS.
-- Migrations and the app both connect as this role; the superuser remains for ops.

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'neatsprint_app') THEN
        CREATE ROLE neatsprint_app LOGIN PASSWORD 'neatsprint_app';
    END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE db_task TO neatsprint_app;
GRANT ALL PRIVILEGES ON DATABASE db_team TO neatsprint_app;

\connect db_task
GRANT CONNECT, CREATE ON DATABASE db_task TO neatsprint_app;
GRANT ALL ON SCHEMA public TO neatsprint_app;
DO $$
DECLARE r record;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER TABLE public.%I OWNER TO neatsprint_app', r.tablename);
    END LOOP;
    FOR r IN SELECT sequencename FROM pg_sequences WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER SEQUENCE public.%I OWNER TO neatsprint_app', r.sequencename);
    END LOOP;
END
$$;

\connect db_team
GRANT CONNECT, CREATE ON DATABASE db_team TO neatsprint_app;
GRANT ALL ON SCHEMA public TO neatsprint_app;
DO $$
DECLARE r record;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER TABLE public.%I OWNER TO neatsprint_app', r.tablename);
    END LOOP;
    FOR r IN SELECT sequencename FROM pg_sequences WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER SEQUENCE public.%I OWNER TO neatsprint_app', r.sequencename);
    END LOOP;
END
$$;
