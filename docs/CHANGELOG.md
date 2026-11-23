# Changelog

All notable changes to NeatSprint are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to
[Semantic Versioning](https://semver.org/).

- **Added** — new capability
- **Changed** — behaviour change
- **Deprecated** — soon to be removed
- **Removed** — removed capability
- **Fixed** — defect fix
- **Security** — security or privacy relevant change
- **Docs** — documentation only

---

## [Unreleased] — MVP development

### Added

- 2026-11-23 — **Tenant isolation at the database**: PostgreSQL RLS on Task/Team tables with
  a tenant-bound session role and per-transaction `app.tenant_id`; M1 is now 34/34.
- 2026-11-23 — **Backlog filters and inline priority editing** with optimistic rollback.
- 2026-11-23 — **Sprint planning and teams admin**: create a sprint, move items between
  backlog and sprint scope, start the sprint, and create/list teams with member counts.
- 2026-11-23 — **Interactive board**: HTML5 drag-and-drop between statuses with optimistic
  updates and rollback, plus an item drawer with description, status moves and comments.
- 2026-11-23 — **Web planning views**: projects list with create, sprint board (read-only) and
  backlog table; nav entry enabled. Seed now creates a team, project, five items and an active
  sprint.
- 2026-11-23 — **Task service**: projects, backlog items with per-project keys, integer
  ranking, status transitions with history, single assignee, comments, sprint create/start/
  complete with carry-over, board and backlog endpoints, internal item lookup.
- 2026-11-23 — **M2 started**: Team service with teams, membership, lead management,
  internal membership lookup for the Task service, RBAC and migrations.
- 2026-11-22 — Added `docs/SETUP_GUIDE.md` (local setup, Google sign-in, CAPTCHA, GitHub settings).
- 2026-11-22 — **M1 final slice**: Google Identity Services ID-token login with invitation-first
  provisioning, invitation duplicate-collapse and resend, optional Turnstile CAPTCHA on auth,
  avatar presign/confirm/read through object storage, and custom role CRUD.
- 2026-11-21 — **M1 completion slice**: transactional outbox + Redis relay (IAM and Core),
  seat-limit enforcement against the tenant plan, password reset with single-use tokens, session
  list/revoke/logout-all, roles matrix and tenant settings/modules admin screens, and silent token
  refresh in the web middleware.
- 2026-11-21 — **M1 identity slice**: IAM schema + migrations, Argon2id credentials, RS256
  access tokens with JWKS, rotating refresh tokens with reuse detection, append-only audit log,
  system roles and the full permission catalogue, invitations with email delivery, and the
  tenant provisioning/bootstrap endpoints.
- 2026-11-21 — **Core tenancy**: tenant schema + migrations, plans, tenant settings, application
  registry, module enablement and the operator provisioning endpoint.
- 2026-11-21 — **Gateway auth**: ForwardAuth to IAM with public auth routes, protected API
  routes and identity header injection.
- 2026-11-21 — **Web auth**: httpOnly cookie BFF, login page, invitation acceptance, admin users
  table with invite form and sign-out.
- 2026-11-21 — `scripts/seed.py` demo tenant/users and `scripts/smoke-auth.py` end-to-end check.

- 2026-11-21 — **M0 foundations**: 15 component repositories created and registered as git
  submodules; Docker Compose stack (Postgres, Redis, object storage, Mailpit, Traefik, 9 services,
  web) verified end to end; Prometheus/Grafana profile with a platform dashboard.
- 2026-11-21 — `neatsprint-contracts` v0.1.0: common OpenAPI components, IAM/Core contracts,
  AsyncAPI event catalogue, Spectral lint.
- 2026-11-21 — `neatsprint-lib` v0.1.1: settings, JSON logging, RFC 7807 errors, request context,
  health/readiness/metrics, async SQLAlchemy primitives, UUIDv7 helpers, tenant-scoped repository.
- 2026-11-21 — `neatsprint-apigw`: Traefik routing, security headers, CORS, rate limits,
  ForwardAuth definition.
- 2026-11-21 — Service template + nine service skeletons (FastAPI, health endpoints, tests,
  Dockerfiles, per-repo CI calling the platform reusable workflow).
- 2026-11-21 — `neatsprint-web`: Next.js 15 shell, design tokens, theme toggle, API client,
  Vitest suite and standalone Docker build.
- 2026-11-21 — Orchestrator automation: bootstrap scripts, Makefile, reusable CI workflows,
  pre-commit, Dependabot, runbook skeleton.

### Docs

- 2026-11-21 — Published the refined documentation set in `docs/`:
  `SCOPE`, `MASTER_PLAN`, `DEVELOPMENT_PLAN`, `TEST_PLAN`, `ARCHITECTURE`, `DATA_MODEL`,
  `API_SPEC`, `SECURITY`, `UI_UX_DESIGN`, `DEVOPS`, `REPOSITORIES`, `DECISIONS`, `GLOSSARY`,
  `CONTRIBUTING`, and this index.
- 2026-11-21 — Added `AGENTS.md` (agent operating guide) and rewrote the root `README.md`.
- 2026-11-21 — Recorded ADR-001…ADR-017, including corrections to contradictory reference
  documents (encryption model, privacy window authority, reporting architecture, device binding).
- 2026-11-21 — Defined the 15 component repositories and the submodule workflow in
  `docs/REPOSITORIES.md`.
- 2026-11-21 — Added ADR-018 (runtime language policy: Python services, Next.js as UI/BFF only,
  Rust for CPU-bound components) in response to the backend-runtime question.
- 2026-11-21 — Clarified ADR-012: a tenant has many users; each account belongs to one tenant with a
  globally unique email. Updated scope, data model, API, security, plans and tests accordingly.

### Changed

- 2026-11-21 — Removed the `minio-init` container; the object-storage image now creates the
  default bucket on first start (`MINIO_DEFAULT_BUCKETS`). One fewer one-shot container.
- 2026-11-21 — Reset the reference roadmap's misleading pre-ticked MVP items; progress now lives
  in `docs/MASTER_PLAN.md` and `docs/DEVELOPMENT_PLAN.md`.

---

## Release History

| Version | Date | Notes |
| :--- | :--- | :--- |
| — | — | No releases yet. `v1.0.0` is the MVP release (milestone M5). |
