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

### Added

- 2026-11-27 - **Unreleased**: Google sign-in failures now name the real cause - a missing
  workspace invitation, an unverifiable token, or a CSRF mismatch - instead of always blaming the
  OAuth configuration.
- 2026-11-27 - **v1.0.7**: Log time gains sprint selection and a tenant "allow time without
  sprint" policy (Core setting, Worklog server-side enforcement); timesheet CSV export includes
  `sprint_id`; fixed the timesheet hydration warning caused by timezone-dependent time formatting;
  72-hour post-launch health window closed with 0 restarts and no P0/P1.
- 2026-11-26 — **v1.0.6**: Google sign-in switched to GSI redirect flow with CSRF check.
- 2026-11-26 — **v1.0.5**: hard navigation after sign-in/sign-out; GSI style CSP fixed.
- 2026-11-26 — **v1.0.4**: Python images apply Debian security upgrades; libzstd advisory cleared.
- 2026-11-26 — **v1.0.3**: reports tenant isolation, database RLS across services, web navigation
  and CSP fixes, PostgreSQL report aggregation; all service tests and web build green.
- 2026-11-24 — **v1.0.2**: team member add/remove UI, signed-in header with sign out, and removed
  the route loading skeletons that left pages stuck on “Loading…”; 22 web tests pass.
- 2026-11-24 — **v1.0.1**: backlog create drawer and BFF POST route; owner create verified,
  viewer `403`; 21 web tests pass.
- 2026-11-24 — **Environment lifecycle docs**: dev and local-staging up/stop/down/rebuild
  commands, profile behaviour, safe "stop everything" procedure and port-conflict troubleshooting
  in `docs/RUNBOOKS.md`.
- 2026-11-24 — **v1.0.0 released**: UAT signed off 9/10 with the desktop item waived under
  ADR-019; release workflow built all 10 images with SBOM + Trivy clean; 72-hour health window
  started (`docs/HEALTH_WINDOW.md`).
- 2026-11-24 — **Local staging + UAT**: offset-port staging profile, web API URL baked at build,
  post-deploy smoke; UAT 9 pass / 1 desktop-blocked. Fixed seed team membership (manager
  tombstone visibility) and MinIO data volume path.
- 2026-11-24 — **Staging smoke + UAT pack**: reusable `scripts/smoke/staging_smoke.py`, deploy
  runbook and pre-UAT evidence in `docs/UAT.md`; staging host still needed.
- 2026-11-24 — **Secret scan**: gitleaks added to platform CI, clean across 70 commits; only
  illustrative JWT examples in frozen reference docs are allowlisted.
- 2026-11-24 — **Target-volume load test**: 100 tenants / 5,157 users / 1M entries; read p95
  267 ms, write p95 77 ms, 0% errors; 1 MiB screenshot upload 38 ms warm; report aggregation
  rewritten in SQL (`docs/LOAD_TEST.md`).
- 2026-11-24 — **Onboarding fix**: `.gitattributes` forces LF for service entrypoints, fixing
  CRLF Windows checkouts; fresh-clone bootstrap + seed + web smoke passed (`docs/ONBOARDING_DRY_RUN.md`).
- 2026-11-24 — **Container/SBOM gate**: all 10 images scanned with Trivy 0.69.3, 0 high/critical;
  web npm CLI removed from runtime stage and stale Python images rebuilt; SBOMs in `docs/sbom/`.
- 2026-11-24 — **Dependency remediation**: Next 16/vitest 5 upgrade cleared web audit findings;
  cryptography upgraded to 50.x in Monitoring; no open high/critical dependency alerts remain.
- 2026-11-24 — **Security hardening follow-up**: Redis-backed login lockout shared across IAM
  replicas, per-service Grafana RED dashboard, merged OpenAPI reference and k6 smoke load test.
- 2026-11-24 — **Upload hardening**: magic-byte sniffing, content/type mismatch rejection,
  optional ClamAV INSTREAM scan, and automatic blob cleanup on rejection.
- 2026-11-24 — **Reliability evidence**: partition maintenance job, backup/restore rehearsal,
  chaos-lite recovery test and GHCR release workflow with SBOM + Trivy.
- 2026-11-24 — **M5 hardening**: cross-tenant probe, CSP/security headers, resource limits,
  Prometheus alerts, runbooks, legal drafts, README/release notes and retrospective.
- 2026-11-24 — **Source backfill**: paginated, resumable report backfill from Task, Worklog and
  Monitoring internal APIs with a CLI command.
- 2026-11-24 — **Accessibility audit**: automated axe tests for the backlog and global search,
  plus skip link, mobile navigation and table scrolling.
- 2026-11-24 — **Export centre**: background CSV/PDF report jobs with status tracking, signed
  downloads, and an export page.
- 2026-11-24 — **Responsive shell**: mobile navigation, skip link, horizontal table scrolling and
  reduced mobile padding.
- 2026-11-24 — **Console completion**: global search and command palette, per-user saved backlog
  views, tenant audit viewer with CSV export, and accessible dashboard/report navigation.
- 2026-11-24 — **Reports service**: rebuildable time/item/monitor/session/sprint facts, replayable
  event projectors with lag status, and cached time/completion/velocity/burndown/monitoring/
  transparency endpoints plus CSV export.
- 2026-11-24 — **Dashboard and reports web**: role-aware home widgets, reports hub, time report,
  Recharts velocity/burndown with data tables, and monitoring heatmap with small-group suppression.
- 2026-11-24 — **Onboarding checklist** on the dashboard.
- 2026-11-24 — **Worklog service**: server-authoritative timer, pause/resume, idle segments,
  manual entries with a 24 h edit window, idempotent offline sync, weekly timesheet aggregation and
  CSV exports via signed URLs.
- 2026-11-24 — **Monitoring service**: device registration and remote commands, monitoring
  sessions/heartbeats, encrypted screenshot ingest, pending/visible privacy window, deletion with
  tombstone and audit, manager gallery with team scope, personal transparency log, promotion and
  retention jobs.
- 2026-11-24 — **Time & privacy web screens**: timesheet week grid with manual entry/export,
  "My screenshots" with countdown and delete, manager monitoring gallery with tombstones, and the
  personal transparency log.
- 2026-11-23 — **Assignment notifications**: Task emits `item.assigned`; IAM stores idempotent
  notifications and exposes list/mark-read/read-all; the web header bell shows unread counts.
- 2026-11-23 — **Digest-safe assignment email template** with batch rendering and escaped content.
- 2026-11-23 — **Shared component library**: DataTable, Drawer, KanbanColumn, StatusBadge,
  PriorityBadge, UserPill and EmptyState, documented with live examples on `/design`.
- 2026-11-23 — **Screen states**: route-level loading skeletons and error boundaries for projects,
  project surfaces and teams; permission-aware "project not available" pages and inline alerts for
  partial data failures.
- 2026-11-23 — **Backlog interactions**: grouping by status/priority/sprint, inline title,
  priority, estimate, assignee and sprint edits, bulk selection with priority/sprint/assignee/
  delete actions, and keyboard navigation (arrows, space, E).
- 2026-11-23 — **Soft delete** endpoint for backlog items (`DELETE /tasks/backlog/{id}`).
- 2026-11-23 — **Assignee validation**: assignments require an active IAM user and, for
  team-scoped projects, membership in a linked team; outsiders get
  `422 assignee_not_eligible`.
- 2026-11-23 — **IAM user lookup** (`POST /internal/users/lookup`): batch, tenant-scoped
  summaries for service-to-service validation.
- 2026-11-23 — **Team membership events** invalidate the Task access cache; membership changes
  apply in seconds instead of waiting for the 60 s TTL.
- 2026-11-23 — **Project access enforcement**: projects with linked teams are visible only to
  members of those teams; managers/admins keep access; denied requests return `404`. Team
  membership is cached for 60 s, project mappings apply immediately.
- 2026-11-23 — **Project team selector** in project settings; saves the task-service mapping.
- 2026-11-23 — **Project-team mapping**: `GET/PUT /tasks/projects/{id}/teams`, verified end to end.
- 2026-11-23 — **Attachment UI**: item drawer lists attachments, uploads via presigned PUT and opens
  time-limited download links.
- 2026-11-23 — **Task attachments**: presigned S3/MinIO upload, confirmation,
  listing and time-limited download links, with MIME and size validation.
- 2026-11-23 — **Team events**: `team.created`, `team.member_added` and
  `team.member_removed` published through the outbox.
- 2026-11-23 — **Task events**: project/item/sprint events written through the outbox and
  published to Redis Streams; verified `item.created` on the stream.
- 2026-11-23 — **Project settings and sprint completion**: edit name/dates/description,
  archive a project, and complete an active sprint with carry-over.
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
