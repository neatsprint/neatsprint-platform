-- Target-volume seed for the load test.
-- Usage:
--   docker compose exec -T postgres psql -U neatsprint -d db_core \
--     -v tenant=<tenant-uuid> -v project=<project-uuid> -f - < scripts/load/seed_volume.sql
--
-- Creates 98 extra tenants, ~5,150 users and 1,000,000 time entries for the
-- supplied tenant/project. Idempotent: rerunning skips existing rows.

\set ON_ERROR_STOP on
\connect db_core
SET synchronous_commit = off;

INSERT INTO tenants (id, name, slug, plan_code, status)
SELECT md5('load-tenant-' || g)::uuid,
       'Load Tenant ' || g,
       'load-tenant-' || g,
       'TEAM',
       'ACTIVE'
FROM generate_series(1, 98) AS g
ON CONFLICT DO NOTHING;

ANALYZE tenants;

\connect db_iam
SET synchronous_commit = off;

INSERT INTO users (id, email, full_name, timezone, locale, status, tenant_id)
SELECT md5('loaduser-main-' || g)::uuid,
       'main-' || g || '@load.neatsprint.local',
       'Load Main ' || g,
       'UTC',
       'en',
       'ACTIVE',
       :'tenant'::uuid
FROM generate_series(1, 250) AS g
ON CONFLICT DO NOTHING;

INSERT INTO users (id, email, full_name, timezone, locale, status, tenant_id)
SELECT md5('loaduser-' || t || '-' || n)::uuid,
       'load-' || t || '-' || n || '@load.neatsprint.local',
       'Load User ' || t || '-' || n,
       'UTC',
       'en',
       'ACTIVE',
       md5('load-tenant-' || t)::uuid
FROM generate_series(1, 98) AS t, generate_series(1, 50) AS n
ON CONFLICT DO NOTHING;

INSERT INTO user_credentials (user_id, password_hash, password_updated_at, must_change)
SELECT u.id,
       (SELECT password_hash FROM user_credentials
         WHERE user_id = (SELECT id FROM users WHERE email = 'owner@acme-labs.com')),
       now(),
       false
FROM users u
WHERE u.email LIKE '%@load.neatsprint.local'
ON CONFLICT DO NOTHING;

ANALYZE users;

\connect db_worklog
SET synchronous_commit = off;

INSERT INTO time_entries (
    id, session_id, user_id, item_id, project_id, started_at, ended_at,
    duration_seconds, source, client_id, tenant_id, created_at, updated_at)
SELECT md5('load-entry-' || g)::uuid,
       NULL,
       md5('loaduser-main-' || (1 + (g % 250)))::uuid,
       NULL,
       :'project'::uuid,
       timestamptz '2026-11-01 00:00:00+00'
           + ((g % 120) || ' days')::interval
           + ((g % 1440) || ' minutes')::interval,
       timestamptz '2026-11-01 00:00:00+00'
           + ((g % 120) || ' days')::interval
           + ((g % 1440) || ' minutes')::interval
           + ((60 + (g % 3540)) || ' seconds')::interval,
       60 + (g % 3540),
       'TIMER',
       md5('load-client-' || g)::uuid,
       :'tenant'::uuid,
       now(),
       now()
FROM generate_series(1, 1000000) AS g
ON CONFLICT DO NOTHING;

ANALYZE time_entries;

\connect db_reports
SET synchronous_commit = off;

INSERT INTO report_time_facts (
    entry_id, user_id, project_id, item_id, started_at, duration_seconds,
    source, updated_at, tenant_id)
SELECT md5('load-entry-' || g)::uuid,
       md5('loaduser-main-' || (1 + (g % 250)))::uuid,
       :'project'::uuid,
       NULL,
       timestamptz '2026-11-01 00:00:00+00'
           + ((g % 120) || ' days')::interval
           + ((g % 1440) || ' minutes')::interval,
       60 + (g % 3540),
       'TIMER',
       now(),
       :'tenant'::uuid
FROM generate_series(1, 1000000) AS g
ON CONFLICT DO NOTHING;

ANALYZE report_time_facts;
