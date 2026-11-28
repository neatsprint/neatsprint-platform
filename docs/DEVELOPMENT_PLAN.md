# NeatSprint — Development Plan

> **Status**: Approved v1.0 · **Version**: 1.0 · **Last updated**: 2026-11-21
> **Owner**: Laksiri Fernando · **Executor**: OpenCade (AI)
> **Parent**: `MASTER_PLAN.md` · **Verification**: `TEST_PLAN.md` · **Requirements**: `SCOPE.md`

This plan is the executable backlog. It is intentionally granular: a task should be completable
and verifiable in one working block. Checkboxes are the source of truth for progress.

---

## 1. How To Use This Plan

- Pick the **first unchecked task** in the current milestone (M0 → M5).
- Do not start a task whose dependencies are unmet.
- Each task ends with: code + tests + docs + checkbox + commit.
- Task ID format: `M<milestone>-T<nn>`. Reference the ID in commit messages, e.g.
  `feat(iam): issue RS256 JWTs with rotation (M1-T07)`.
- If a task grows beyond one block, split it in place (`M1-T07a`) rather than working invisibly.
- If an unforeseen dependency appears, update this plan **before** coding around it.

### Status board

| Milestone | Tasks | Done | State |
| :--- | ---: | ---: | :--- |
| M0 Foundations | 24 | 21 | 21 done · 2 moved to M1 · 1 partial |
| M1 Identity & Tenancy | 34 | 34 | Complete |
| M2 Work Management | 33 | 33 | 33 done · M2 complete |
| M3 Time, Monitoring & Desktop | 40 | 25 | 25 done · desktop agent pending |
| M4 Reports & Console | 26 | 26 | 26 done · M4 complete |
| M5 Hardening & Launch | 28 | 27 | 27 done · 72h window pending |
| P2 Collaboration | 22 | 0 | Deferred |
| P3 Intelligence | 16 | 0 | Deferred |
| Cross-cutting (X-01…07) | 7 | 0 | Continuous |

---

## 2. Engineering Conventions

### 2.1 Branching

| Branch | Use |
| :--- | :--- |
| `main` | Always releasable; protected |
| `feat/<area>-<slug>` | Feature work; one logical change |
| `fix/<area>-<slug>` | Defects |
| `chore/<slug>` | Tooling, docs, deps |

Squash-merge into `main` with a Conventional Commit title. Submodule bumps are a separate commit
in the orchestrator (`chore(submodules): bump iam to v0.3.1`).

### 2.2 Commit types

`feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `revert`, `security`.

### 2.3 Contract-first workflow

1. Write the endpoint in the service's OpenAPI source (or the contracts repo for cross-service).
2. Generate/commit the spec; open a draft PR.
3. Implement against the spec; generate TS client for the web app.
4. Contract tests run in CI and fail on drift.

### 2.4 Service template invariants

Every FastAPI service ships with:

```text
src/
  api/            routers only — validation, auth deps, response models
  core/           domain logic, pure functions, no SQL
  db/             models, repositories, migrations
  clients/        typed HTTP clients for other services
  events/         publishers/consumers, outbox handlers
  settings.py     pydantic-settings, 12-factor
  main.py         app factory, middleware, /healthz, /readyz, /metrics
tests/
  unit/ integration/ contract/
migrations/
Dockerfile  pyproject.toml  .env.example  README.md
```

### 2.5 Definition of Done (restated)

Acceptance criteria met · tests green · lint/types/secrets clean · contract updated · migration
present · tenant-scope and permission checks reviewed · docs/checkbox/changelog · commit pushed.

---

## 3. Milestone M0 — Foundations

**Goal**: a clean machine can start the stack, see a health check, and run the test template.

### Epic M0-E1 — Workspace & repositories

- [x] **M0-T01** Add `.gitmodules` and the 15 component submodules under `services/` once Laksiri
  creates the remotes. *AC*: `git submodule status` lists all, each pinned to `main` HEAD.
  *Dep*: none (blocked on human repo creation).
- [x] **M0-T02** Create `services/README.md` explaining submodule workflow (init, update, bump).
  *AC*: a newcomer can follow the commands without help.
- [x] **M0-T03** Add root `Makefile` with `bootstrap`, `up`, `down`, `logs`, `migrate`, `seed`,
  `test`, `lint`, `e2e`, `clean`. *AC*: targets documented in `make help`.
- [x] **M0-T04** Add `.editorconfig`, `.gitattributes` (LF normalisation), and update root
  `.gitignore` for Python, Node, Rust, Docker, IDE and secrets. *AC*: `git status` clean after
  running the stack.

### Epic M0-E2 — Shared libraries & service template

- [x] **M0-T05** Publish `neatsprint-contracts` bootstrap: `common.yaml` (error model, pagination,
  headers), `iam.yaml`, `core.yaml` placeholders, README. *AC*: specs pass `spectral lint`.
- [x] **M0-T06** Build shared Python package `neatsprint-lib` (installed as a git dependency or
  private index): settings base, JSON logging, correlation middleware, RFC 7807 errors, UUIDv7
  helper, pagination, health router, tenant context, permission dependency. *AC*: unit tested.
- [x] **M0-T07** Build `neatsprint-lib-db`: async SQLAlchemy session factory, base model with
  audit columns, tenant-scoped repository mixin, Alembic env template, transaction helper.
  *AC*: a demo table migrates up/down in tests.
- [ ] **M0-T08** *(moved to M1 — first producer lands with IAM events)* Build
  `neatsprint-lib-events`: transactional outbox table, publisher to Redis Streams, consumer base
  with idempotency and retry/DLQ. *AC*: integration test proves exactly-once handling under
  duplicate delivery.
- [x] **M0-T09** Create the reference service template repo content (cookiecutter or script
  `scripts/new-service.py`) generating the §2.4 layout. *AC*: generated service passes `make test`.

### Epic M0-E3 — Orchestration

- [x] **M0-T10** Write `docker-compose.yml` with postgres:16, redis:7, minio, mailpit, gateway,
  10 services, web. *AC*: `docker compose config` valid; all containers healthy.
- [x] **M0-T11** Add `infra/traefik/` static + dynamic config: entrypoints, `/api/v1` routers,
  ForwardAuth middleware, security headers, CORS, rate limit middlewares. *AC*: unknown route
  returns 404 JSON; `/healthz` reachable through gateway.
- [x] **M0-T12** Add `docker-compose.observability.yml` with Prometheus, Grafana (provisioned
  datasource + starter dashboard), Loki + Promtail. *AC*: service metrics visible in Grafana.
- [x] **M0-T13** Add `scripts/bootstrap.ps1` and `scripts/bootstrap.sh`: create `.env` from
  example, start the stack and wait for every health endpoint. *AC*: idempotent.
  *(RS256 dev keys, migrations and seed move to M1 with the first schema.)*
- [x] **M0-T14** Write `.env.example` covering every variable used by compose and services, with
  comments and safe defaults. *AC*: no secret values; compose starts with only these values.

### Epic M0-E4 — CI & quality tooling

- [x] **M0-T15** Create reusable GitHub Actions workflow `service-ci.yml`: ruff, mypy, pytest with
  postgres+redis services, coverage gate, docker build, Trivy scan. *AC*: runs on template repo.
- [x] **M0-T16** Create `web-ci.yml`: eslint, tsc, vitest, playwright smoke, build. *AC*: passes on
  skeleton.
- [x] **M0-T17** Add pre-commit config (ruff, prettier, trailing whitespace, secret scan,
  conventional commit lint). *AC*: `pre-commit run --all-files` clean.
- [x] **M0-T18** Add dependency update automation (Dependabot/Renovate) config for all repos.
  *AC*: PRs open weekly, grouped.
- [x] **M0-T19** Add `docs/CHANGELOG.md` with Keep-a-Changelog format and the update rule in
  `CONTRIBUTING.md`.

### Epic M0-E5 — Web shell

- [x] **M0-T20** Scaffold Next.js 15 app: App Router, TypeScript strict, Tailwind, shadcn/ui init,
  design tokens from `UI_UX_DESIGN.md`. *AC*: `pnpm build` succeeds; tokens visible in Storybook or
  a `/design` page.
- [x] **M0-T21** Implement app shell: sidebar, topbar, tenant badge, user menu, theme toggle,
  responsive drawer. *AC*: keyboard navigable; passes axe smoke.
- [x] **M0-T22** Add API client generation from OpenAPI (`openapi-typescript`) and a typed fetch
  wrapper with error mapping. *AC*: type errors surface at build time.

### Epic M0-E6 — Data & seed

- [ ] **M0-T23** *(moved to M1 — requires IAM/Core schemas)* Write seed script: 1 tenant
  (`Acme Labs`), 6 users (owner/admin/manager/lead/member/viewer), 2 teams, 2 projects, 1 active
  sprint, 20 backlog items, sample time entries. *AC*: rerunnable without duplicates.
- [x] **M0-T24** Write `docs/RUNBOOKS.md` skeleton (start/stop, reset DB, rotate dev keys, logs).

**M0 exit gate**: `docker compose up -d` → every `/healthz` green through the gateway → web shell
renders → contracts lint clean → CI green on an empty PR → ADR-001…004, 007–009, 013, 014,
018 accepted. *Seeded login and outbox are delivered with M1 because they need the first schema.*

---

## 4. Milestone M1 — Identity & Tenancy

**Goal**: invite → register → login → correct authorisation, end to end.

### Epic M1-E1 — IAM data & security core

- [x] **M1-T01** IAM schema + migration: `users`, `user_credentials`, `social_accounts`,
  `sessions`, `invitations`, `roles`, `permissions`, `role_permissions`, `user_roles`,
  `api_keys`, `audit_log`. *AC*: constraints, indexes, **globally unique `email`** (ADR-012),
  tenant index on every tenant-owned table.
- [x] **M1-T02** Seed system roles and the full permission catalogue from `SECURITY.md` §5.
  *AC*: matrix test asserts every role's permission set.
- [x] **M1-T03** Implement Argon2id password hashing + policy (min length, breach list stub).
  *AC*: unit tests for hashing, verification, rehash-on-parameter-change.
- [x] **M1-T04** Enforce tenant scoping at the database with PostgreSQL RLS on Task and Team
  tables (owner role `neatsprint_app`, `app.tenant_id` set per transaction). *AC*: an unscoped
  query returns no rows; API access still works.
- [x] **M1-T05** Implement append-only audit log writer (actor, action, target, before/after hash,
  request id, IP, user agent). *AC*: updates/deletes rejected by DB trigger.

### Epic M1-E2 — Authentication

- [x] **M1-T06** `POST /api/v1/auth/login` with device metadata, lockout after N failures, and
  generic error messages. *AC*: returns access+refresh; failures audited.
- [x] **M1-T07** RS256 JWT issuance with claims `sub`, `tid`, `roles`, `scope`, `jti`, `exp`,
  `device_id`; JWKS endpoint; key rotation support (two active kids). *AC*: verified by a third
  party library; rotation test passes.
- [x] **M1-T08** `POST /auth/refresh` with rotation + reuse detection (revoke family on reuse).
  *AC*: replaying an old refresh token revokes the session family.
- [x] **M1-T09** `POST /auth/logout`, `GET /auth/me`, session listing and revoke-all.
  *AC*: revoked tokens fail until expiry.
- [x] **M1-T10** Google sign-in via Identity Services ID tokens: signature/audience/issuer
  verification, invitation-first provisioning, account linking. *AC*: mocked-token verification
  tests. *(Domain auto-join is a tenant setting but enrolment stays invitation-first for MVP.)*
- [x] **M1-T11** Password reset request + confirm with single-use token (30 min).
  *AC*: token reuse rejected; old sessions invalidated.
- [x] **M1-T12** Rate limiting and CAPTCHA hook on auth endpoints. *AC*: 429 after threshold.

### Epic M1-E3 — Invitations & users

- [x] **M1-T13** Create/list/revoke/resend invitations with hashed tokens and expiry; reject an
  email already held by another tenant with neutral `409 email_unavailable`. *AC*: duplicate
  pending invite collapses to one; no tenant disclosure.
- [x] **M1-T14** Accept invitation: validates token, creates user, assigns roles/teams, marks
  accepted, logs audit. *AC*: idempotent on double submit.
- [x] **M1-T15** Email adapter (SMTP/Mailpit in dev, SES in prod) with templated invite/reset
  emails, plain-text fallback. *AC*: rendered emails snapshot-tested.
- [x] **M1-T16** User profile CRUD (`/iam/users`), avatar upload to object storage (presigned),
  timezone/locale. *AC*: self vs admin field-level permissions enforced.
- [x] **M1-T17** Deactivate/reactivate user: revoke sessions, emit `user.deactivated` event.
  *AC*: deactivated user cannot authenticate or refresh.
- [x] **M1-T18** Role assignment endpoints with privilege-escalation guard. *AC*: manager cannot
  grant `ADMIN`; owner can.
- [x] **M1-T19** Custom role CRUD (stored, returned by API), UI deferred to P3.
  *AC*: invalid permission string rejected.

### Epic M1-E4 — Core tenancy

- [x] **M1-T20** Core schema: `plans`, `tenants`, `tenant_settings`, `applications`,
  `application_features`, `tenant_applications`. *AC*: seeded applications list.
- [x] **M1-T21** `GET/PATCH /core/tenants/current` including all settings from SCOPE FR-TEN-05.
  *AC*: validation ranges enforced; changes audited.
- [x] **M1-T22** Application registry endpoints; enable/disable module with plan check.
  *AC*: disabled module returns `403 module_disabled` from its own service.
- [x] **M1-T23** Plan limit resolver (users, projects, retention) with cached lookup in Redis and
  invalidation on change. *AC*: limits enforced on create paths.
- [x] **M1-T24** Tenant provisioning script/endpoint for operator use (create tenant + owner
  invite). *AC*: produces a working login in one command.
- [x] **M1-T25** Emit `tenant.created`, `tenant.settings_changed`, `tenant.module_toggled`.

### Epic M1-E5 — Enforcement

- [x] **M1-T26** Implement `require_permission("task:item:create")` dependency and
  `require_tenant` dependency in the shared lib; wire into IAM and Core first. *AC*: 403 body uses
  stable codes; unit tested.
- [x] **M1-T27** Gateway ForwardAuth integration: validate token, inject trusted headers, strip
  inbound spoofed headers. *AC*: spoofed `X-User-ID` is discarded.
- [x] **M1-T28** Service-side JWKS validation middleware (defence in depth). *AC*: invalid
  signature rejected even if the gateway is bypassed in tests.

### Epic M1-E6 — Web: authentication & admin

- [x] **M1-T29** Login page, Google button, error states, "remember me" semantics, accessible form.
  *AC*: matches `UI_UX_DESIGN.md` S-01; keyboard + screen-reader tested.
- [x] **M1-T30** Invitation acceptance and password reset pages. *AC*: expired/invalid token states.
- [x] **M1-T31** Session handling: httpOnly cookies via BFF route handlers, silent refresh,
  logout, route middleware protection. *AC*: no tokens in localStorage.
- [x] **M1-T32** Admin → Users: table, filters, invite dialog, role assignment, deactivate.
  *AC*: controls hidden without permission and rejected by API.
- [x] **M1-T33** Admin → Roles: read-only system role matrix view. *AC*: matrix generated from API.
- [x] **M1-T34** Admin → Tenant settings: general, monitoring policy, retention, modules.
  *AC*: saves and reloads; validation messages inline.

**M1 exit gate**: fresh tenant → invite → accept → login as each of the six roles → permission
matrix verified by automation → audit entries present for invite, login, role change.

---

## 5. Milestone M2 — Work Management

**Goal**: plan a sprint, run a board, complete a sprint.

### Epic M2-E1 — Task service foundation

- [x] **M2-T01** Task schema: `projects`, `project_teams`, `backlog_items`, `item_comments`,
  `item_history`, `sprints`, `sprint_items`, `item_attachments`. *AC*: FKs within service only;
  logical refs for `user_id`/`team_id`.
- [x] **M2-T02** Project CRUD with key generation (unique per tenant), archive semantics.
  *AC*: archived project read-only; key immutable.
- [x] **M2-T03** Project access resolver (project teams ∪ project members ∪ tenant-wide perms),
  cached per request. *AC*: used by every list/detail endpoint.
- [x] **M2-T04** Backlog item CRUD with type/status/priority validation and item key
  (`PRJ-123`). *AC*: sequence per project is concurrency-safe.
- [x] **M2-T05** Ranking service using lexicographic keys; reorder endpoint. *AC*: 100 concurrent
  reorders produce no duplicate ranks (property test).
- [x] **M2-T06** Status transition machine + `item_history` entries with actor and timestamp.
  *AC*: illegal transition returns 422 with code.
- [x] **M2-T07** Single-assignee rule with unassign endpoint. *AC*: second assignee rejected.
- [x] **M2-T08** Comments: create/edit/delete (soft), mentions parsed into `mentioned_user_ids`.
  *AC*: edit history preserved; mention event emitted.
- [x] **M2-T09** Attachments: presigned upload, MIME/size validation, download authorisation.
  *AC*: cross-tenant attachment fetch denied.

### Epic M2-E2 — Sprints

- [x] **M2-T10** Sprint CRUD + state machine (`PLANNED → ACTIVE → COMPLETED`), one active per
  project enforced by partial unique index. *AC*: starting a second returns 409.
- [x] **M2-T11** Sprint planning: add/remove items, commit snapshot (points/hours at start).
  *AC*: snapshot immutable after start.
- [x] **M2-T12** Complete sprint: close, record velocity inputs, carry-over dialog data
  (done/moved/backlog). *AC*: idempotent completion.
- [x] **M2-T13** Emit `project.created`, `item.created/updated/transitioned`, `sprint.started/
  completed` to the outbox.

### Epic M2-E3 — Team service

- [x] **M2-T14** Team schema (`teams`, `team_members`) with lead flag. *AC*: unique membership.
- [x] **M2-T15** Team CRUD + membership endpoints with lead-vs-admin permissions.
  *AC*: removing the last lead is blocked or reassigns.
- [x] **M2-T16** Project ↔ team mapping API consumed by Task service (cached). *AC*: project team
  change invalidates task access cache.
- [x] **M2-T17** Emit `team.member_added/removed` events; consume in Task cache invalidation.

### Epic M2-E4 — Cross-service integrity

- [x] **M2-T18** IAM client library: validate user ids, fetch minimal user summaries in batch.
  *AC*: circuit breaker + timeout; cached 60 s.
- [x] **M2-T19** Authorisation guard for "assignee must be an active member of a project team".
  *AC*: assigning an outsider returns 422.
- [x] **M2-T20** Contract tests for Task ↔ Team ↔ IAM client interactions.

### Epic M2-E5 — Web: planning surfaces

- [x] **M2-T21** Projects list: cards/table, search, filter, archived toggle, create dialog.
- [x] **M2-T22** Project settings: name, key, dates, teams, archive.
- [x] **M2-T23** Backlog view: grouped table, inline edit, bulk select, priority chips, sprint
  assignment, keyboard navigation.
- [x] **M2-T24** Board view: columns by status, drag-and-drop with optimistic update and rollback,
  swimlane by assignee (optional), WIP indicator.
- [x] **M2-T25** Item detail drawer: description editor, comments, history timeline, attachments,
  time summary placeholder (populated in M3).
- [x] **M2-T26** Sprint planning view: backlog on the left, sprint on the right, capacity bar.
- [x] **M2-T27** Sprint board header: dates, progress, complete-sprint dialog with carry-over.
- [x] **M2-T28** Teams admin: list, create, members, lead assignment.
- [x] **M2-T29** Empty, loading, error and permission-denied states for every M2 screen.
- [x] **M2-T30** Component library additions: DataTable, Drawer, KanbanColumn, PriorityBadge,
  UserPill, EmptyState. *AC*: documented in the design page.

### Epic M2-E6 — Notifications stub

- [x] **M2-T31** In-app notification model in IAM/notification stub for assignment events
  (bell menu). *AC*: mark-as-read persists.
- [x] **M2-T32** Assignment notification email template (digest-safe).
- [x] **M2-T33** Seed update: realistic multi-sprint history for reports testing.

**M2 exit gate**: create project → 20 items → plan sprint → drag through states → complete with
carry-over; access control verified for outsider, viewer and member.

---

## 6. Milestone M3 — Time Tracking, Monitoring & Desktop Agent

**Goal**: trustworthy tracking and provably honest privacy controls.

### Epic M3-E1 — Worklog service

- [x] **M3-T01** Schema: `work_sessions`, `time_entries`, `idle_segments`. *AC*: partitions on
  `started_at` created by migration.
- [x] **M3-T02** `POST /work/start`, `/work/stop`, `GET /work/current` with server-authoritative
  session state and one-active-timer rule. *AC*: concurrent start returns 409 with current session.
- [x] **M3-T03** Monotonic duration calculation: client sends elapsed monotonic seconds; server
  clamps against wall clock and flags anomalies. *AC*: clock rollback cannot add time.
- [x] **M3-T04** Manual time entries with edit window and audit trail.
- [x] **M3-T05** Idempotent `POST /work/sync` batch endpoint keyed by client UUIDv7.
  *AC*: replay of the same batch creates no duplicates.
- [x] **M3-T06** Idle handling API: accept/truncate idle segment, recompute totals.
- [x] **M3-T07** Timesheet query endpoint (week view, totals by day/project/item).
- [x] **M3-T08** CSV export job with permission gating and signed URL.
- [x] **M3-T09** Emit `work.session_started/stopped`, `time_entry.recorded` events.

### Epic M3-E2 — Monitoring service

- [x] **M3-T10** Schema: `devices`, `monitoring_sessions`, `screenshots`, `activity_heartbeats`,
  `deletion_audit`. *AC*: weekly partitions for screenshots.
- [x] **M3-T11** Device registration: accept public key, bind to user, return `device_id`;
  list/revoke devices. *AC*: revoked device cannot upload.
- [x] **M3-T12** KMS envelope encryption adapter (dev: local key file; prod: AWS KMS/age key):
  encrypt on ingest, decrypt only for authorised views. *AC*: round-trip test; key id stored.
- [x] **M3-T13** Screenshot upload (multipart or presigned PUT) with session validation, quota,
  dedupe hash, and `pending` state. *AC*: oversize/invalid type rejected.
- [x] **M3-T14** Privacy window engine: `visible_after = captured_at + window`; list endpoints
  filter by state per role. *AC*: manager cannot fetch pending images.
- [x] **M3-T15** Deletion endpoint: authorise owner + inside window, delete blob, null path,
  set tombstone, write audit, emit `screenshot.deleted`. *AC*: second delete returns 204
  idempotently; blob absent in storage test.
- [x] **M3-T16** Background job: promote pending → visible after window (or on explicit user
  approval), emit `screenshot.available`.
- [x] **M3-T17** Retention job: hard delete expired blobs + metadata + `ai_embeddings` refs.
- [x] **M3-T18** Heartbeat ingest + session activity aggregation (active/idle minutes).
- [x] **M3-T19** Manager gallery query with tombstone placeholders and view-audit logging.
- [x] **M3-T20** Personal transparency endpoint: my captures, my deletions, my sessions.
- [x] **M3-T21** Remote device controls: suspend/revoke/wipe commands queued for agent pickup.

### Epic M3-E3 — Desktop agent foundation

- [x] **M3-T22** Tauri v2 workspace: React UI + Rust core, IPC commands, tray icon, single
  instance, auto-start option. *AC*: builds on Windows CI; dev hot reload documented. Done
  2026-11-28: `neatsprint-desktop@5e7a713`, CI run `46155877720` green (Prettier, ESLint,
  `cargo fmt`, `clippy -D warnings`, tests, `tauri build --debug`); tray, close-to-tray and
  single instance verified on the built exe; hot reload documented in the desktop README.
- [x] **M3-T23** Login + device registration; key pair generation (Ed25519); private key in OS
  keychain; signed request nonce. *AC*: token theft alone cannot be replayed from another device.
  Done 2026-11-28: Ed25519 key pair in Windows Credential Manager, `POST /auth/device-session`
  issues a `did`-bound token, ForwardAuth verifies the per-request proof and rejects reused
  nonces; 12-check probe green (no proof, replay, wrong key, device mismatch, refresh binding,
  unbound web token unaffected) and the agent's `device_probe` example passes. The access token
  stays in memory because Credential Manager caps an entry at 2560 bytes; only the refresh token
  is at rest.
- [x] **M3-T24** SQLCipher local DB with Argon2id-derived key, schema for `local_tasks`,
  `pending_worklogs`, `pending_screenshots`, `sync_state`. *AC*: raw file unreadable; key never on
  disk unwrapped. Done 2026-11-28: SQLCipher via `rusqlite` + vendored OpenSSL, random 32-byte DB
  key sealed with AES-256-GCM under an Argon2id KEK (wrap secret in the OS keychain), envelope in
  `db.key`. Verified: plain SQLite reports "file is not a database"; schema names absent from the
  raw file; the key does not appear in the envelope; round-trip test covers reopen and state.
- [x] **M3-T25** Timer module: start/stop/switch, monotonic clock, idle detection hook, crash-safe
  resume. *AC*: kill process mid-session → resume reconciles correctly. Done 2026-11-28: state
  machine persisted in SQLCipher (`state`, `started_at`, `last_seen_at`, `accumulated_ms`,
  `item_id`), 1 s heartbeat with a 10 s grace window, `GetLastInputInfo` idle hook, and stop
  enqueues a `pending_worklogs` row. Verified by 4 unit tests and a cross-process probe: start,
  heartbeat at 3 s, kill, 14 s later status reports **Paused / 3 s elapsed** (no dead time),
  then stop queues one entry.
- [x] **M3-T26** Task list + quick switch UI, sync from server. Done 2026-11-28: `sync_tasks` pulls
  `/auth/me`, projects and each backlog through signed requests, filters items assigned to the
  user and upserts them into `local_tasks`; the agent lists cached tasks ordered in progress → to
  do → review → blocked → done, click-to-select, and Start binds the selected `item_id`. Verified
  live: two assigned AUTH items cached and read back in order; unit test covers ordering and
  upsert-in-place.
- [x] **M3-T27** Capture engine: randomised interval, multi-monitor selection, DPI-correct,
  encrypt-at-capture to temp store. *AC*: 30-minute soak produces expected count, no leaks. Done
  2026-11-28: GDI capture per selected monitor (DPI-awareness v2), 3–7 min randomised interval,
  worker gated on a running timer and idle < 5 min, AES-256-GCM encrypt-before-disk with a keychain
  key, rows in `pending_screenshots`, cleanup removing deleted rows and orphan blobs. Verified: 10
  tests including a **30-minute simulated soak** (6 frames, rows == files, cleanup removes the
  deleted frame); real probe captured 1920×1080, 1.69 MB ciphertext, decrypts to a PNG, cleaned up.
  A real-time 30-minute soak on the staging machine remains the final gate item.
- [x] **M3-T28** Review tray: gallery of pending screenshots, preview (decrypt in memory), delete with
  confirmation, countdown to window close. Done 2026-11-28: grid of pending captures with countdown
  and size, preview decrypted in memory, downscaled to 480 px and sent as a data URL (no plaintext on
  disk), delete with confirmation destroys blob and row, privacy window pulled from
  `/monitor/policy` (24 h default). Verified by 3 tests and a real probe: 1 frame, 24 h remaining,
  125 KB preview, delete left 0 pending.
- [ ] **M3-T29** Sync engine: queue worker, exponential backoff, batch sizes, conflict resolution,
  server-sent new-task pull, sync status UI.
- [ ] **M3-T30** Transparency log file (readable by user) of every event sent.
- [ ] **M3-T31** Remote control handling: suspend/revoke/wipe.
- [ ] **M3-T32** Signed updater (Ed25519) with version monotonicity and staged rollout flag.
- [ ] **M3-T33** Windows installer (MSI) + code-signing pipeline (dev cert; prod cert via owner).
- [ ] **M3-T34** macOS build pipeline (unsigned dev build; notarisation deferred to owner).
- [ ] **M3-T35** Crash reporting with opt-in and PII scrubbing (Sentry-compatible DSN).
- [ ] **M3-T36** Agent diagnostics screen: version, last sync, capture state, permission status.

### Epic M3-E4 — Web: time & monitoring

- [x] **M3-T37** Timesheet screen: week grid, add manual entry, edit, totals, export button.
- [x] **M3-T38** "My screenshots" gallery: pending/visible tabs, delete action with countdown,
  empty state explaining the privacy window.
- [x] **M3-T39** Manager monitoring view: user/date filters, session timeline, thumbnail grid,
  tombstone cards, view-audit note.
- [x] **M3-T40** Personal transparency log screen.

**M3 exit gate**: 4-hour offline capture+sync test passes; delete-screenshot test proves blob and
embedding removal while manager sees tombstone; device revoke and wipe verified.

---

## 7. Milestone M4 — Reports, Dashboards & Console Polish

### Epic M4-E1 — Reports service

- [x] **M4-T01** Read-model database schema (`report_time_facts`, `report_item_facts`,
  `report_monitor_facts`, `report_sprint_snapshots`). *AC*: rebuildable from scratch.
- [x] **M4-T02** Event consumers + projectors with replay support and lag metric.
- [x] **M4-T03** Backfill command from source services (paginated, resumable).
- [x] **M4-T04** `GET /reports/time` (by project/user/team/date). *AC*: reconciles with raw entries.
- [x] **M4-T05** `GET /reports/completion` (created vs completed).
- [x] **M4-T06** `GET /reports/velocity` (last N sprints).
- [x] **M4-T07** `GET /reports/burndown` (sprint scope vs remaining).
- [x] **M4-T08** `GET /reports/monitoring` (sessions, active/idle, captures, deletions, rate).
  *AC*: aggregation mode hides rows below threshold.
- [x] **M4-T09** `GET /reports/transparency` (personal log).
- [x] **M4-T10** Export jobs: CSV immediate, PDF async (HTML template → headless render) with
  signed URL + expiry; job status endpoint.
- [x] **M4-T11** Report caching layer keyed by filter hash with tenant-scoped invalidation.

### Epic M4-E2 — Web: dashboards & reports

- [x] **M4-T12** Dashboard, role-aware: my day (timer summary, assigned items), team pulse,
  sprint progress, privacy summary for self.
- [x] **M4-T13** Reports hub with report cards and date-range picker.
- [x] **M4-T14** Time report screen with stacked bar + table + CSV export.
- [x] **M4-T15** Velocity + burndown screens with chart library chosen from UI plan (Recharts).
- [x] **M4-T16** Monitoring summary screen with heatmap and deletion rate, respecting aggregation.
- [x] **M4-T17** Export centre: job list, status, download.
- [x] **M4-T18** Charts accessibility: data table alternative, colour-safe palette, no 3D.

### Epic M4-E3 — Console completion

- [x] **M4-T19** Global search (items, projects, people) with keyboard shortcut.
- [x] **M4-T20** Saved views for backlog/board (per user).
- [x] **M4-T21** Command palette (Ctrl/⌘+K): navigate, create item, start timer link.
- [x] **M4-T22** Audit log viewer with filters and export (admin only).
- [x] **M4-T23** Notification centre (in-app) with unread badge.
- [x] **M4-T24** Onboarding checklist for new tenants (invite team, create project, start timer).
- [x] **M4-T25** Full responsive pass (tablet, narrow laptop), dark mode contrast fixes.
- [x] **M4-T26** Accessibility pass: axe clean, keyboard traps removed, focus order, ARIA labels,
  reduced-motion support.

**M4 exit gate**: reports reconcile with source data; all MVP screens present with empty/loading/
error states; axe and manual keyboard audit pass; visual QA against `UI_UX_DESIGN.md`.

---

## 8. Milestone M5 — Hardening & Launch

### Epic M5-E1 — Security

- [x] **M5-T01** Threat model workshop output committed (`SECURITY.md` §2 updated with findings).
- [x] **M5-T02** OWASP ASVS L2 self-assessment; fix all high/critical gaps.
- [x] **M5-T03** Cross-tenant penetration script executed; results recorded.
- [x] **M5-T04** Auth hardening review: token lifetimes, rotation, lockout, CSRF, cookie flags.
- [x] **M5-T05** Upload hardening: content sniffing, size limits, virus scan integration.
- [x] **M5-T06** Dependency + container scan zero high/critical; SBOM generated.
- [x] **M5-T07** Secrets rotation runbook + KMS key rotation rehearsal.

### Epic M5-E2 — Reliability & performance

- [x] **M5-T08** Load test at target scale (k6): API mix, screenshot upload, reports.
  *AC*: NFR-PERF targets met, error rate < 0.1%.
- [x] **M5-T09** Database review: indexes, slow query log, partition maintenance job.
- [x] **M5-T10** Backup/restore rehearsal with documented RTO/RPO evidence.
- [x] **M5-T11** Chaos-lite: kill a service, verify gateway error shape and recovery.
- [x] **M5-T12** Resource limits and health probes for every container.

### Epic M5-E3 — Operations

- [x] **M5-T13** Prometheus alerts: error rate, latency, queue lag, disk, backup failure, cert
  expiry. *AC*: each alert has a runbook link.
- [x] **M5-T14** Grafana dashboards: platform overview, per-service RED, business KPIs.
- [x] **M5-T15** `docs/RUNBOOKS.md` complete: start/stop/restore/rotate/incident/on-call.
- [x] **M5-T16** Release pipeline: versioned images, changelog, GitHub release, rollback.
- [x] **M5-T17** Staging environment provisioned; smoke suite runs post-deploy.

### Epic M5-E4 — Legal & documentation

- [x] **M5-T18** `legal/terms-of-service.md`, `privacy-policy.md`, `dpa.md`,
  `subprocessors.md`, `monitoring-disclosure-template.md`, `README.md`.
- [x] **M5-T19** Update root `README.md`: features, architecture, quick start, repo map, status.
- [x] **M5-T20** Publish API reference (Redoc/Scalar) from contracts.
- [x] **M5-T21** Contributor onboarding guide verified by a clean-clone dry run.
- [x] **M5-T22** `docs/RELEASE_NOTES.md` for v1.0.0.

### Epic M5-E5 — Acceptance

- [x] **M5-T23** Execute UAT script with Laksiri; record pass/fail per SCOPE §8 item.
- [x] **M5-T24** Fix UAT defects (timeboxed; critical only).
- [x] **M5-T25** Sign-off recorded in `agent/conversation.md`; tag `v1.0.0`.
- [x] **M5-T26** Post-launch monitoring window (72 h) with daily health report. Closed
  2026-11-27 19:12 +05:30: 0 restarts, 0 tracebacks, 2 `502`s during a deliberate redeploy, no
  P0/P1. Daily lines in `docs/HEALTH_WINDOW.md`.
- [x] **M5-T27** Retrospective: what to change in M0–M5 for P2/P3.
- [x] **M5-T28** Update MASTER_PLAN with P2 kickoff checklist.

**M5 exit gate**: SCOPE §8 satisfied, signed off, `v1.0.0` released (`v1.0.1` and `v1.0.2` patch
releases shipped on 2026-11-24).

### 8.1 Post-v1.0.2 Required Improvements (Patch Backlog)

Identified during the post-v1.0.2 architectural, code and documentation review. Execute in order of
severity before starting Phase 2:

- [x] **IMP-T01 (S1 Security / Tenant Isolation — Reports)**: In `neatsprint-reports`
  `GET /reports/burndown` (`src/neatsprint_reports/api/router.py:275`), verify
  `snapshot.tenant_id == principal.tenant_id` (or query with `tenant_id`) so a foreign tenant's
  `sprint_id` cannot leak sprint start/end dates. Also emit `item.deleted` from `neatsprint-task`
  `delete_item` and handle `item.deleted` in `neatsprint-reports` `projector.py` so deleted items
  are removed from `report_item_facts`. *AC*: cross-tenant burndown test returns empty/default
  dates; deleting an item removes it from report facts.
- [x] **IMP-T02 (S2 Security / Database RLS)**: Extend PostgreSQL Row-Level Security (RLS) from
  `db_task` and `db_team` to `db_reports`, `db_worklog`, `db_monitoring`, and tenant-owned tables
  in `db_iam`. *AC*: migrations enable and force RLS with `app.tenant_id` policy; unscoped queries
  return 0 rows.
- [x] **IMP-T03 (S2 Web UX & RBAC Gaps)**:
  1. Enable `Reports` (`href: "/reports", enabled: true`) in the desktop sidebar navigation
     (`services/neatsprint-web/src/components/app-shell.tsx:52`).
  2. Pass `canCreate={profile.permissions.includes("task:item:create")}` from
     `projects/[id]/backlog/page.tsx` to `BacklogClient` so `MEMBER` users (who have
     `task:item:create` but not `task:item:edit`) can create backlog items.
  3. Add the **Settings** tab link (`/projects/${id}/settings`) to the project sub-navigation on
     `projects/[id]/board/page.tsx`, `backlog/page.tsx`, and `planning/page.tsx`.
  4. Poll or fetch `/api/session/work/current` in `AppShell` so the topbar timer pill reflects an
     active timer instead of hardcoded `"No timer running"`.
  *AC*: Vitest component tests cover all four fixes.
- [x] **IMP-T04 (S2 Web CSP & Google Sign-In)**: Update `Content-Security-Policy` in
  `services/neatsprint-web/next.config.ts` to allow `https://accounts.google.com/gsi/client` in
  `script-src`, `https://accounts.google.com` in `frame-src`/`connect-src`, and dynamic
  `NEXT_PUBLIC_API_BASE_URL` / S3 origins so Google Sign-In and staging ports (`:8100`, `:9100`)
  produce zero CSP console errors. *AC*: browser console on `/login` has 0 CSP errors.
- [ ] **IMP-T05 (S2 Reports SQL Aggregation & Redis Cache)**: Rewrite `completion_report`,
  `velocity_report`, `burndown_report` and `monitoring_report` in `neatsprint-reports` to use
  PostgreSQL `GROUP BY`/`SUM` instead of loading all fact rows into Python memory, and move
  `neatsprint_reports/services/cache.py` from an in-process dictionary to Redis with stampede
  protection. *AC*: all report endpoints pass unit/integration tests and stay < 300 ms at target
  volume.
- [ ] **IMP-T06 (S3 Gateway RFC 7807 Error Pages & Rate-Limit Headers)**: Configure Traefik error
  middleware in `neatsprint-apigw` so upstream `502`/`503` failures return RFC 7807 JSON
  (`503 dependency_unavailable`) instead of plain-text `Bad Gateway`, and emit `RateLimit-*` /
  `Retry-After` headers (`API_SPEC.md` §1.6).
- [ ] **IMP-T07 (S3 API Idempotency & Optimistic Concurrency)**: Implement `Idempotency-Key`
  request replay/conflict handling (`409 idempotency_key_reused`) on mutating endpoints and
  `If-Match`/`ETag` version checks on `PATCH /tasks/backlog/{id}` (`API_SPEC.md` §1.1, §1.5).
- [ ] **IMP-T08 (S2 Automated Authz Route-Registration & Playwright E2E CI)**: Add a FastAPI
  route-inspector test in every service asserting 100% of routes declare a permission or public
  allow-list entry (`SECURITY.md` §16), extend `scripts/security/cross_tenant_probe.py` to cover
  Reports and Monitoring endpoints, and wire Playwright E2E critical journeys into CI.
- [ ] **IMP-T09 (S3 Makefile & Tooling Alignment)**: Add missing `migrate` and `seed` targets to the
  root `Makefile` (`M0-T03`) and add an `npm run lint` script in `services/neatsprint-web/package.json`.
- [ ] **IMP-T10 (S3 Legal Footer Links & GDPR DSAR Endpoints)**: Render and link `/legal/terms`,
  `/legal/privacy` and `/legal/dpa` from the web login/app footer (`SECURITY.md` §16,
  `TEST_PLAN.md` §11), and add self-service GDPR export/erasure endpoints (`SCOPE.md` `NFR-SEC-07`).

---

## 9. Phase 2 — Collaboration (deferred)

Kept here so the design does not accidentally preclude it.

- [ ] **P2-T01** Chat schema (`chat_channels`, `chat_messages`, `chat_reads`) + migration.
- [ ] **P2-T02** Channel CRUD bound to project teams; membership from Team service.
- [ ] **P2-T03** Message send/history/edit/delete with mention parsing and rate limits.
- [ ] **P2-T04** WebSocket gateway with JWT handshake, presence, typing, fan-out via Redis.
- [ ] **P2-T05** Client-type icons from heartbeat/connection metadata.
- [ ] **P2-T06** Daily scrum post template and reminder job.
- [ ] **P2-T07** Notification service extraction; in-app, email, push token registry.
- [ ] **P2-T08** Mobile: Expo project, auth + biometrics, assigned list, item detail.
- [ ] **P2-T09** Mobile: status update, manual time, offline queue.
- [ ] **P2-T10** Mobile: chat, push notifications, deep links.
- [ ] **P2-T11** Remote timer stop from mobile.
- [ ] **P2-T12** GitHub App: link commits/PRs to item keys, status sync.
- [ ] **P2-T13** E2E + app store release pipelines.
- [ ] **P2-T14** Public API keys + webhooks for tenants.
- [ ] **P2-T15** Load test chat fan-out; tune connection limits.
- [ ] **P2-T16** Chat moderation/reporting controls.
- [ ] **P2-T17** Notification preferences UI.
- [ ] **P2-T18** Docs: chat, mobile, integrations.
- [ ] **P2-T19** Security review of WebSocket auth and mobile storage.
- [ ] **P2-T20** App Store / Play Store submissions.
- [ ] **P2-T21** P2 acceptance test pass.
- [ ] **P2-T22** P2 retrospective + P3 kickoff.

---

## 10. Phase 3 — Intelligence (deferred)

- [ ] **P3-T01** AI service scaffold, provider adapter (OpenAI/Anthropic/Gemini), prompt registry.
- [ ] **P3-T02** pgvector schema + embedding pipeline for permitted text (items, comments, logs).
- [ ] **P3-T03** RAG retrieval with strict tenant + permission filters.
- [ ] **P3-T04** On-behalf-of auth so AI never exceeds the caller's permissions.
- [ ] **P3-T05** `POST /ai/ask` with streaming (SSE) and citations.
- [ ] **P3-T06** Work summary + standup draft generation.
- [ ] **P3-T07** Backlog assistant: draft item, estimate suggestion, confirmation-gated write.
- [ ] **P3-T08** Deletion hooks: purge embeddings on screenshot/task deletion.
- [ ] **P3-T09** AI audit log (prompt, tools, sources, response) with admin viewer.
- [ ] **P3-T10** PII scrubbing before provider calls; zero-retention provider settings.
- [ ] **P3-T11** Quotas, cost tracking per tenant, kill switch.
- [ ] **P3-T12** Voice push-to-talk (local STT first, Whisper fallback).
- [ ] **P3-T13** Custom role builder UI.
- [ ] **P3-T14** Legal hold + SIEM export.
- [ ] **P3-T15** Stripe billing (plans, seats, invoices, webhooks).
- [ ] **P3-T16** Gmail integration (task from email, digest).

---

## 11. Cross-Cutting Tasks (run continuously)

- [ ] **X-01** Keep `docs/` in sync with code in the same PR that changes behaviour.
- [ ] **X-02** Update `docs/CHANGELOG.md` for every user-visible change.
- [ ] **X-03** Bump submodule pins in the orchestrator after each service release.
- [ ] **X-04** Monthly dependency and base-image refresh.
- [ ] **X-05** Quarterly restore drill and access review.
- [ ] **X-06** Maintain seed data as the product grows (new tables get seeds).
- [ ] **X-07** Record every architectural deviation as an ADR before merging.

---

## 12. Plan Change Log

| Date | Change | Reason |
| :--- | :--- | :--- |
| 2026-11-21 | Plan v1 created | Initial planning cycle |
| 2026-11-21 | M0 executed; T08 (outbox) and T23 (seed) moved to M1 because they depend on the first schemas | Delivered foundation scope |
| 2026-11-21 | M1 first slice delivered: IAM auth/RBAC/invitations/audit, Core tenancy/settings/modules, ForwardAuth, web login/admin, seed | Vertical auth slice verified end to end |
| 2026-11-21 | M1 second slice: outbox/Redis, seat limits, password reset, session management, roles matrix, settings/modules UI, silent refresh | 28/34 tasks done |
| 2026-11-22 | M1 final slice: Google ID-token login, invitation collapse/resend, CAPTCHA hook, avatar presign/confirm, custom role CRUD. T04 moved to M2 for RLS | 33/34 tasks done |
| 2026-11-23 | M2 started: Team service (schema, migration, CRUD, membership, internal lookup, RBAC) | 2/33 tasks done |
| 2026-11-23 | Task service: projects, backlog items, ranking, transitions/history, comments, sprints/start/complete | 12/33 tasks done |
| 2026-11-23 | Web projects list/create, read-only board and backlog, planning seed | 14/33 tasks done |
| 2026-11-23 | Board drag-and-drop transitions with optimistic rollback, item drawer with comments and status moves | 16/33 tasks done |
| 2026-11-23 | Sprint planning UI and teams admin | 18/33 tasks done |
| 2026-11-23 | RLS tenant isolation on Task/Team tables; M1 complete 34/34 | M1 gate closed |
