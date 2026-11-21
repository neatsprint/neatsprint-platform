-- One logical database per service on a single cluster (ADR-002).
-- Migrations live in each service repository and run as a pre-deploy job.

CREATE DATABASE db_iam;
CREATE DATABASE db_core;
CREATE DATABASE db_task;
CREATE DATABASE db_team;
CREATE DATABASE db_worklog;
CREATE DATABASE db_monitoring;
CREATE DATABASE db_chat;
CREATE DATABASE db_reports;
CREATE DATABASE db_ai;

-- Extensions needed by the platform. pgcrypto is available in the base image;
-- pgvector is installed by the AI service image/migration when Phase 3 starts.
\connect db_iam
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

\connect db_task
CREATE EXTENSION IF NOT EXISTS pg_trgm;
