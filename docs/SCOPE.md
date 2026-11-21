# NeatSprint — Project Scope

> **Status**: Draft v1 for review · **Version**: 1.0 · **Last updated**: 2026-11-21
> **Owner**: Laksiri Fernando (Project Owner / Architect) · **Author**: OpenCade (AI)
> **Supersedes**: `documents/scope.md` (kept as reference)
> **Companion documents**: `MASTER_PLAN.md`, `ARCHITECTURE.md`, `SECURITY.md`, `DATA_MODEL.md`

---

## 1. Product Definition

NeatSprint is a **multi-tenant SaaS platform** for agile delivery, with three tightly integrated
clients:

- **Web application** — planning, boards, reporting, administration, monitoring review.
- **Desktop agent** — the primary work surface: task timer, idle detection, privacy-first
  screenshots, offline capture and automatic sync.
- **Mobile application** — on-the-go visibility and lightweight actions.

Its differentiators are (a) **honest monitoring** — the employee can inspect and delete their own
screenshots, and deletion is auditable; and (b) an **application-agnostic core** — the tenancy,
identity and permission model can host future enterprise applications (ERP, APS, production
planning) without redesign.

### 1.1 Product Principles

| # | Principle | Consequence |
| :--- | :--- | :--- |
| P1 | **Tenant isolation is absolute** | Every tenant-owned record and query is scoped; isolation is tested continuously |
| P2 | **Privacy is a feature, not a policy page** | Deletion of a screenshot is real, immediate, irreversible and auditable |
| P3 | **The employee can always see what is recorded** | Visible recording indicator, personal transparency log |
| P4 | **Offline must never lose work** | Client-generated UUIDv7 + durable local queue + idempotent sync |
| P5 | **Permissions, not roles, decide access** | Feature-level permission strings enforced server-side |
| P6 | **One task, one owner** | A backlog item has at most one assignee at any time |
| P7 | **Boring, proven technology** | Fewer moving parts until scale proves otherwise |
| P8 | **Open core, commercial cloud** | AGPLv3 source; hosted service adds billing, SLA, compliance |

---

## 2. Personas & Roles

| Persona | Primary goals | Default system role |
| :--- | :--- | :--- |
| **Tenant Owner** | Owns the subscription, billing and organisation | `OWNER` |
| **Tenant Admin** | Manages users, roles, projects, policies | `ADMIN` |
| **Project Manager** | Plans sprints, assigns work, reviews delivery | `MANAGER` |
| **Team Lead** | Runs the team's day-to-day board and reviews | `LEAD` |
| **Team Member** | Executes tasks, tracks time, collaborates | `MEMBER` |
| **Stakeholder / Auditor** | Reads reports and audit trails, no mutation | `VIEWER` |
| **AI Agent** (service) | Answers questions and drafts changes on behalf of a user | `AI_AGENT` (non-human) |

> **Tenancy cardinality (important)**: a tenant has **many users**, each of whom logs in and works
> independently. The restriction is the other direction: a **user account belongs to exactly one
> tenant**. Within that tenant a user may join many teams and work across many projects. A person
> who genuinely needs two workspaces needs two accounts with different email addresses in MVP
> (ADR-012); single-login multi-tenant access is a later feature, not a constraint on how many
> people can use a tenant.

---

## 3. Scope Boundaries

### 3.1 In Scope — MVP (Phase 1)

| Area | Included |
| :--- | :--- |
| Tenancy | Tenant provisioning, plan assignment, tenant settings, application enablement |
| Identity | Email/password, Google OAuth2/OIDC, invitations, password reset, session refresh |
| Authorization | System roles, custom roles, feature permissions, server-side enforcement |
| Projects | Project CRUD, project settings, project ↔ team mapping |
| Backlog | Items of type `TASK`, `STORY`, `BUG`, `SUGGESTION`; status, priority, estimate, comments, attachments |
| Sprints | Create/start/complete sprint, sprint backlog, carry-over |
| Teams | Team CRUD, membership, project assignment |
| Time tracking | Desktop timer, idle detection, manual entries, timesheet view, CSV export |
| Monitoring | Random screenshots while timer runs, privacy window, deletion, tombstone audit |
| Desktop agent | Tray app, login, device registration, offline queue, auto-update, integrity checks |
| Web app | Dashboard, board, backlog, sprint, timesheet, screenshot gallery, admin console |
| Reports | Time by project/user, task completion, sprint velocity, burndown, screenshot/deletion summary |
| Platform | Gateway, observability baseline, backups, seed data, developer onboarding |

### 3.2 In Scope — Later Phases (specified, not built in MVP)

| Phase | Area |
| :--- | :--- |
| Phase 2 | Team chat + presence, daily scrum flow, notifications, mobile app (Expo), remote timer control, GitHub integration |
| Phase 3 | AI assistant (RAG), work summaries, voice commands, anomaly detection, custom-role builder UI, legal hold, SIEM export, billing via Stripe, Gmail integration |

### 3.3 Explicitly Out of Scope

- Payroll, invoicing, accounting, expense management.
- Document management / wiki (links to external tools only).
- HR performance appraisal scoring or ranking of employees.
- Global cross-tenant administration, tenant data migration tooling.
- On-premise air-gapped installation for MVP (Docker-based self-host is supported).
- Native smart-TV / wearable clients, browser extension, always-on audio capture.
- Video recording or keystroke content logging (keystroke *activity counts* only).

---

## 4. Functional Requirements

Requirement IDs are stable and referenced by the development and test plans.
Priority: **M** = must (MVP), **S** = should (MVP if time allows), **C** = could (later phase).

### 4.1 Tenancy & Applications

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-TEN-01 | A tenant is created with a name, unique slug, plan tier and lifecycle status (`TRIAL`, `ACTIVE`, `SUSPENDED`, `CLOSED`). | M |
| FR-TEN-02 | A global application registry lists installable modules (e.g. `TASK_MGMT`, `MONITORING`, `CHAT`, `REPORTS`, `AI_ASSISTANT`). Applications are shared across tenants. | M |
| FR-TEN-03 | Tenant administrators can enable or disable modules for their tenant; disabled modules are invisible in UI and rejected by the API. | M |
| FR-TEN-04 | Plan limits (max users, max active projects, screenshot retention) are enforced at the API layer. | M |
| FR-TEN-05 | Tenant settings include timezone, week start, screenshot interval, privacy window, retention days, aggregation mode. | M |
| FR-TEN-06 | The Owner can transfer ownership and close the tenant; closure schedules data erasure per retention policy. | S |

### 4.2 Identity, Onboarding & Session

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-IAM-01 | Users authenticate with email + password (Argon2id hashes). | M |
| FR-IAM-02 | Users authenticate with Google (OAuth2/OIDC); accounts are just-in-time provisioned only when the email domain or an existing invitation matches the tenant. | M |
| FR-IAM-03 | Authorised users invite colleagues by email; the invitation carries a single-use, time-limited token bound to the tenant and optional initial team/roles. | M |
| FR-IAM-04 | Invitees accept by setting a password (or via Google) and are linked to the tenant and initial team. | M |
| FR-IAM-05 | Invitations expire after a configurable period (default 7 days) and can be revoked or resent. | M |
| FR-IAM-06 | Access tokens are RS256 JWTs (15 min); refresh tokens are rotated on every use (7 days) with reuse detection. | M |
| FR-IAM-07 | Users can request a password reset by email; reset tokens are single-use and expire in 30 minutes. | M |
| FR-IAM-08 | Admins can deactivate a user. Deactivation revokes all sessions and stops monitoring immediately. | M |
| FR-IAM-09 | Every user has a profile: full name, email, avatar, job title, timezone, locale, notification preferences. | M |
| FR-IAM-10 | Multi-factor authentication (TOTP) for admin roles. | S |
| FR-IAM-11 | SSO via SAML/OIDC for enterprise tenants. | C |
| FR-IAM-12 | A tenant supports many users up to its plan seat limit; each user authenticates independently and can access the tenant concurrently. | M |

### 4.3 Roles & Permissions

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-RBAC-01 | Six immutable system roles exist: `OWNER`, `ADMIN`, `MANAGER`, `LEAD`, `MEMBER`, `VIEWER`. | M |
| FR-RBAC-02 | Permissions are feature-level strings `domain:resource:action` (see `docs/SECURITY.md` §5). | M |
| FR-RBAC-03 | A user may hold multiple roles; effective permissions are the additive union, minus explicit denies. | M |
| FR-RBAC-04 | A user cannot grant a role or permission they do not themselves hold (privilege-escalation guard). | M |
| FR-RBAC-05 | Role and permission changes are written to the immutable audit log within the same transaction. | M |
| FR-RBAC-06 | The API denies by default; absence of a required permission returns `403` with a stable error code. | M |
| FR-RBAC-07 | Custom roles composed from permissions, with a live permission-preview in the admin UI. | C |

### 4.4 Projects, Backlog & Sprints

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-PRJ-01 | A project has a key (uppercase, unique per tenant), name, description, owner, status, start/end dates, and one or more teams. | M |
| FR-PRJ-02 | Archiving a project is soft: the data remains readable, becomes read-only, and is excluded from default views. | M |
| FR-PRJ-03 | Every backlog item belongs to exactly one project and has a type (`TASK`, `STORY`, `BUG`, `SUGGESTION`). | M |
| FR-PRJ-04 | A backlog item has title, rich-text description, status, priority, estimate (points), labels, reporter, optional assignee (max one), sprint (optional), due date. | M |
| FR-PRJ-05 | Items can be reordered within a backlog with a durable rank; concurrent reorders must not duplicate rank (fractional/lexicographic ranking). | M |
| FR-PRJ-06 | A task's status flow is `TODO → IN_PROGRESS → IN_REVIEW → DONE`, plus `BLOCKED`; transitions are validated server-side and recorded as history. | M |
| FR-PRJ-07 | Comments support plain text with mentions, edits (with history) and soft delete. | M |
| FR-PRJ-08 | A sprint belongs to a project, has a name, goal, start/end date, state (`PLANNED`, `ACTIVE`, `COMPLETED`) and a committed set of items. | M |
| FR-PRJ-09 | Only one sprint per project may be `ACTIVE`. Starting a sprint snapshots committed scope. | M |
| FR-PRJ-10 | Completing a sprint moves `DONE` items to history and offers carry-over of unfinished items. | M |
| FR-PRJ-11 | Assignment typically happens at sprint planning but is permitted at any time; unassigned items may exist in the backlog. | M |
| FR-PRJ-12 | Users see only projects they are entitled to (project membership, team membership, or tenant-wide permission). | M |
| FR-PRJ-13 | Attachments (files ≤ 25 MB) are stored in object storage with type/size validation and virus scanning in Phase 2. | S |
| FR-PRJ-14 | Sub-tasks / checklists, dependencies, epics, custom fields. | C |

### 4.5 Teams

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-TEM-01 | Teams have a name, description, lead and members. | M |
| FR-TEM-02 | A team can be assigned to multiple projects; a project can have multiple teams. | M |
| FR-TEM-03 | Removing a member from a team revokes team-scoped visibility immediately (effective on next authorization check). | M |
| FR-TEM-04 | Team leads can add/remove members without tenant-admin rights. | M |
| FR-TEM-05 | Nested teams / squads-of-squads. | C |

### 4.6 Time Tracking

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-WRK-01 | A user can start a timer against one backlog item at a time. Starting a second timer requires stopping the first (explicit prompt). | M |
| FR-WRK-02 | Timer state is authoritative on the server; the desktop agent reconciles state on reconnect. | M |
| FR-WRK-03 | Elapsed time uses a monotonic clock locally and server-side reconciliation, so system-clock changes cannot inflate time. | M |
| FR-WRK-04 | Idle detection: after the configured idle threshold the timer is paused and the user is asked to keep or discard the idle segment. | M |
| FR-WRK-05 | Manual time entries (date, duration, item, comment) can be created and edited for the current user; edits are audited. | M |
| FR-WRK-06 | Offline entries are queued locally, synced idempotently, and de-duplicated by client-generated UUIDv7. | M |
| FR-WRK-07 | A weekly timesheet shows planned vs actual per item, with totals per day and project. | M |
| FR-WRK-08 | CSV export of timesheets (per user/team/project/date range) is permission-gated. | M |
| FR-WRK-09 | Approvals workflow for timesheets (submit/approve/reject). | C |

### 4.7 Monitoring & Privacy

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-MON-01 | Screenshots are captured at randomised intervals only while a timer is running; the interval range is set by tenant policy. | M |
| FR-MON-02 | The agent shows a persistent recording indicator and a toast at capture time; there is no hidden mode. | M |
| FR-MON-03 | Users can view their own screenshots in a personal gallery. | M |
| FR-MON-04 | Users can permanently delete their own screenshots until the privacy window closes (default 24 h, configurable 1 h–72 h). | M |
| FR-MON-05 | Deletion destroys the object blob and any derived AI embedding within one minute; the metadata row becomes a tombstone (`deleted_by_user = true`, blob path nulled). | M |
| FR-MON-06 | Managers see tombstoned entries as "Deleted by user at <time>" and can never retrieve the image. | M |
| FR-MON-07 | Every deletion and every manager view of a screenshot is written to an append-only audit log. | M |
| FR-MON-08 | Screenshots become visible to managers only after the privacy window closes (pending → visible). | M |
| FR-MON-09 | Retention: screenshots are hard-deleted after the tenant retention period (default 30 days). | M |
| FR-MON-10 | Activity heartbeat (active/idle) is recorded per session for reporting; it contains no content. | M |
| FR-MON-11 | Tenant-level "aggregation mode" hides per-individual metrics when the team is smaller than the configured threshold. | S |
| FR-MON-12 | Window-title capture is optional, off by default, and visible to the user when on. | C |

### 4.8 Reporting & Analytics

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-RPT-01 | Time by project, by user and by team for a date range. | M |
| FR-RPT-02 | Task completion: created vs completed per period, per project. | M |
| FR-RPT-03 | Sprint velocity across the last N sprints. | M |
| FR-RPT-04 | Sprint burndown (remaining estimate vs ideal line). | M |
| FR-RPT-05 | Monitoring summary: sessions, active time, idle time, screenshots captured, screenshots deleted, deletion rate. | M |
| FR-RPT-06 | Personal transparency log for each user: what was captured and what was deleted. | M |
| FR-RPT-07 | CSV export for all MVP reports; PDF export for the executive summary. | S |
| FR-RPT-08 | All reports obey RBAC scope (own / team / tenant) and tenant aggregation mode. | M |
| FR-RPT-09 | Report queries never block transactional traffic (read-model database). | M |

### 4.9 Desktop Agent

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-DSK-01 | Tray-first app; start/stop timer, switch task, open review tray, log out. | M |
| FR-DSK-02 | Device registration: generates a key pair, registers the public key, stores the private key in the OS keychain. | M |
| FR-DSK-03 | Signed updates only (Ed25519), with rollback protection via monotonic version numbers. | M |
| FR-DSK-04 | Offline mode: captures time and screenshots, queues everything encrypted, syncs with exponential backoff. | M |
| FR-DSK-05 | Local database is encrypted with SQLCipher; the key is derived via Argon2id and wrapped in the OS keychain. | M |
| FR-DSK-06 | Screen capture honours multi-monitor and DPI scaling; users choose which displays are captured. | M |
| FR-DSK-07 | Remote controls from admin: suspend (pause capture), revoke (log out), wipe (destroy local data). | M |
| FR-DSK-08 | Agent self-reports health (version, last sync, capture status) so managers can detect disabled agents. | M |
| FR-DSK-09 | Local audit file the user can read: every event sent to the server. | S |
| FR-DSK-10 | Linux packaging (AppImage/deb). | S |

### 4.10 Web Application

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-WEB-01 | Responsive web app, light and dark themes, WCAG 2.1 AA, keyboard-navigable boards. | M |
| FR-WEB-02 | Screens: login, invitation acceptance, dashboard, projects, backlog, board, sprint, timesheet, screenshot gallery, reports, team, settings, audit log. | M |
| FR-WEB-03 | Real-time-ish updates via polling in MVP; WebSockets in Phase 2 with chat. | M |
| FR-WEB-04 | Optimistic UI for drag/drop and status changes with rollback on error. | M |
| FR-WEB-05 | Every list supports filter, sort, search and saved views (per user). | S |
| FR-WEB-06 | Command palette (Ctrl/⌘+K) for navigation and quick create. | S |

### 4.11 Chat, Notifications & Integrations (Phase 2+)

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-CHT-01 | One persistent channel per project team, with history and mentions. | C (P2) |
| FR-CHT-02 | Presence indicators derived from desktop heartbeat, showing client type. | C (P2) |
| FR-CHT-03 | Daily scrum post format with yesterday/today/blockers. | C (P2) |
| FR-NOT-01 | In-app and email notifications for assignment, mention, invitation, sprint start/end. | C (P2) |
| FR-INT-01 | GitHub: link commits and pull requests to backlog items by key. | C (P2) |
| FR-INT-02 | Gmail: create a task from an email / receive digests. | C (P3) |
| FR-INT-03 | Public REST API with tenant-scoped API keys and webhooks. | S |

### 4.12 Mobile App (Phase 2)

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-MOB-01 | Login with biometric unlock, secure token storage. | C (P2) |
| FR-MOB-02 | View assigned projects, items and notifications. | C (P2) |
| FR-MOB-03 | Update item status and log manual time. | C (P2) |
| FR-MOB-04 | Start/stop the desktop timer remotely ("stop my timer"). | C (P2) |
| FR-MOB-05 | Team chat and push notifications. | C (P2) |

### 4.13 AI (Phase 3, enterprise)

| ID | Requirement | Pri |
| :--- | :--- | :--- |
| FR-AI-01 | Natural-language questions over the user's permitted project data (RAG). | C (P3) |
| FR-AI-02 | Draft backlog items and improve descriptions/estimates, always with explicit confirmation before writing. | C (P3) |
| FR-AI-03 | Work summaries / standup drafts from logs, commits and item history. | C (P3) |
| FR-AI-04 | AI inherits the requesting user's permissions exactly (on-behalf-of); it can never exceed them. | C (P3) |
| FR-AI-05 | Deleted screenshots are never processed; embeddings are destroyed on deletion. | C (P3) |
| FR-AI-06 | Every AI prompt, tool call, source and response is audit-logged. | C (P3) |
| FR-AI-07 | Voice input via push-to-talk only; no always-listening capture. | C (P3) |

---

## 5. Non-Functional Requirements

### 5.1 Performance & Capacity

| ID | Requirement |
| :--- | :--- |
| NFR-PERF-01 | p95 read API latency < 300 ms at the gateway for MVP data volumes (100 tenants, 5,000 users, 1M work logs). |
| NFR-PERF-02 | p95 write API latency < 500 ms excluding file upload. |
| NFR-PERF-03 | Screenshot upload accepted < 2 s for a 1 MB encrypted image on a 10 Mbps link. |
| NFR-PERF-04 | Web app Largest Contentful Paint < 2.5 s on a mid-range laptop over broadband. |
| NFR-PERF-05 | Reports for a 250-person tenant return in < 5 s (cached) / < 30 s (cold, async export). |
| NFR-PERF-06 | Desktop agent idle CPU < 2% average, working set < 250 MB. |

### 5.2 Reliability & Availability

| ID | Requirement |
| :--- | :--- |
| NFR-REL-01 | Cloud target 99.9% monthly availability for the API; single-region for MVP. |
| NFR-REL-02 | RPO ≤ 15 min, RTO ≤ 4 h for the primary database. |
| NFR-REL-03 | Offline capture supports ≥ 7 days / 5,000 events without data loss. |
| NFR-REL-04 | All write endpoints are idempotent on a client-supplied key; retries never duplicate entries. |
| NFR-REL-05 | Graceful degradation: if reports or AI are down, core planning and tracking still work. |

### 5.3 Security & Privacy

| ID | Requirement |
| :--- | :--- |
| NFR-SEC-01 | TLS 1.3 in transit; AES-256 at rest for databases, object storage and backups. |
| NFR-SEC-02 | Tenant isolation verified by automated cross-tenant tests on every PR (see TEST_PLAN). |
| NFR-SEC-03 | No secrets in source; secret scanning blocks merges. |
| NFR-SEC-04 | OWASP ASVS Level 2 baseline; dependency and container scanning in CI. |
| NFR-SEC-05 | Audit log is append-only and retained ≥ 1 year. |
| NFR-SEC-06 | Personal data minimisation: no keystroke contents, no audio, no camera, no clipboard capture. |
| NFR-SEC-07 | GDPR: access, export, erasure and restriction requests supported within 30 days. |

### 5.4 Usability & Accessibility

| ID | Requirement |
| :--- | :--- |
| NFR-UX-01 | WCAG 2.1 AA: contrast ≥ 4.5:1, full keyboard operation, visible focus, screen-reader labels. |
| NFR-UX-02 | A new user can start tracking time within 3 minutes of first login. |
| NFR-UX-03 | A manager can find "who worked on what last week" in ≤ 3 clicks. |
| NFR-UX-04 | UI available in English (MVP); strings externalised for future locales. |

### 5.5 Maintainability & Operability

| ID | Requirement |
| :--- | :--- |
| NFR-MNT-01 | ≥ 80% line coverage on domain/business logic; 100% coverage of permission checks. |
| NFR-MNT-02 | Every service exposes `/healthz` (liveness) and `/readyz` (readiness), plus `/metrics`. |
| NFR-MNT-03 | All services emit structured JSON logs with correlation/trace IDs. |
| NFR-MNT-04 | One-command local stack (`docker compose up`) with seeded demo data. |
| NFR-MNT-05 | Reproducible builds; pinned dependency lockfiles for every component. |

### 5.6 Compliance & Licensing

| ID | Requirement |
| :--- | :--- |
| NFR-CMP-01 | Core source under AGPLv3; commercial terms for the hosted service in `legal/`. |
| NFR-CMP-02 | Privacy policy, DPA and sub-processor list published before public launch. |
| NFR-CMP-03 | Data residency documented per region; EU hosting available for EU tenants (post-MVP). |

---

## 6. Data Ownership & Key Entities

The platform is the processor of tenant data; the tenant is the controller.

| Domain | Entities (owned by service) |
| :--- | :--- |
| Identity | `users`, `user_credentials`, `social_accounts`, `sessions`, `invitations`, `roles`, `permissions`, `role_permissions`, `user_roles`, `api_keys`, `audit_log` |
| Tenancy | `tenants`, `applications`, `application_features`, `tenant_applications`, `tenant_settings`, `plans` |
| Work | `projects`, `project_teams`, `backlog_items`, `item_comments`, `item_history`, `sprints`, `sprint_items`, `item_attachments` |
| People | `teams`, `team_members` |
| Time | `work_sessions`, `time_entries`, `idle_segments` |
| Monitoring | `monitoring_sessions`, `screenshots`, `activity_heartbeats`, `devices` |
| Reports | `report_*` projections (rebuildable) |
| Chat (P2) | `chat_channels`, `chat_messages`, `chat_reads` |
| AI (P3) | `ai_conversations`, `ai_messages`, `ai_summaries`, `ai_embeddings`, `ai_audit_log` |

Detailed columns, keys and indexes: `docs/DATA_MODEL.md`.

---

## 7. Assumptions

1. Tenants are organisations; consumer/freelancer use is a tenant of one.
2. A tenant has unlimited users (subject to plan seats). A **user account** is bound to one tenant,
   and email addresses are globally unique across the platform so login is unambiguous. A person
   needing two workspaces uses two accounts/emails (revisit only if demand appears — would require
   a workspace selector and an identity/tenancy redesign).
3. Email delivery is available (SES/SMTP); Google OAuth credentials are provisioned by the owner.
4. Screen capture is legal in the tenant's jurisdiction and disclosed in their employment terms;
   NeatSprint supplies the mechanism and transparency, not the legal basis.
5. MVP runs single-region; multi-region and data residency are post-MVP.
6. Billing is manual (plan assignment by the platform operator) in MVP; Stripe integration is Phase 3.
7. Desktop MVP targets Windows 10/11 first, macOS second, Linux best-effort.
8. English-only UI in MVP.
9. Scale assumptions: 100 tenants, 5,000 users, 2,000 concurrent desktop agents, 1M time entries.
10. AI features are enterprise-gated and use a commercial LLM provider selected in Phase 3.

---

## 8. MVP Acceptance Criteria (Release Gate)

The MVP may be released only when **all** are true:

1. A new tenant can be provisioned, seeded with an owner, and invite a member end-to-end in the
   hosted environment.
2. Every permission in the MVP matrix is enforced server-side and verified by automated tests.
3. Tenant isolation is verified by a cross-tenant test suite and one manual adversarial review.
4. A desktop user can track 4 hours offline (including screenshots) and sync with zero data loss
   or duplicates.
5. A user can delete a screenshot and an independent check confirms the blob and any derived
   embedding are gone while the manager still sees a tombstone.
6. Reports reconcile with raw time entries (hour totals match to the second).
7. Backup restore is rehearsed successfully and documented.
8. Load test at NFR-PERF targets passes with error rate < 0.1%.
9. Security checklist (OWASP ASVS L2 items in scope) is complete; no high/critical findings open.
10. Documentation set in `docs/` is current, and `README.md` quick start works on a clean machine.

---

## 9. Key Metrics (Product Health)

| Metric | Target |
| :--- | :--- |
| Time from invite to first tracked minute | < 10 min (median) |
| Weekly active desktop agents / licensed users | > 80% |
| Screenshot deletion rate | monitored, not punished; > 30% triggers a product review |
| Sync failure rate | < 0.5% of queued items |
| Support tickets per 100 users / month | < 5 |
| API error rate (5xx) | < 0.1% |

---

## 10. Dependencies & Constraints

- **Team**: Laksiri (owner/architect) + AI agent(s). This constrains parallel work; the plan
  sequences vertically rather than horizontally.
- **Repositories**: multi-repo with git submodules; each service has its own CI (see
  `docs/REPOSITORIES.md`). Repository creation is a human step.
- **Licensing**: AGPLv3 for the core; all dependencies must be licence-compatible
  (no AGPL-incompatible SaaS-only libraries).
- **Third parties**: Google OAuth, email provider, object storage, (Phase 3) LLM provider,
  (Phase 3) Stripe. Each is isolated behind an adapter.
- **Legal**: employee-monitoring disclosure templates, DPA, privacy policy required before public
  launch (milestone M5).

---

## 11. Traceability

| Requirement group | Design | Development | Test |
| :--- | :--- | :--- | :--- |
| FR-TEN / FR-IAM / FR-RBAC | `ARCHITECTURE.md` §4, `SECURITY.md` §3–5 | M1 | TS-01, TS-02 |
| FR-PRJ / FR-TEM | `ARCHITECTURE.md` §5, `DATA_MODEL.md` §4 | M2 | TS-03 |
| FR-WRK / FR-DSK / FR-MON | `ARCHITECTURE.md` §6, `SECURITY.md` §6 | M3 | TS-04, TS-06 |
| FR-RPT | `ARCHITECTURE.md` §7, `DATA_MODEL.md` §7 | M4 | TS-05 |
| FR-WEB | `UI_UX_DESIGN.md` | M1–M4 | TS-07 |
| FR-CHT / FR-MOB / FR-NOT | `ARCHITECTURE.md` §8 | P2 | TS-08 |
| FR-AI | `ARCHITECTURE.md` §9, `SECURITY.md` §8 | P3 | TS-09 |
| NFR-* | `SECURITY.md`, `DEVOPS.md` | M0, M5 | TS-10, TS-11 |

---

## 12. Open Questions for Laksiri

These do not block documentation work; answers shape M1–M3. Defaults in brackets are what the
plan currently assumes.

| # | Question | Default if unanswered |
| :--- | :--- | :--- |
| Q1 | Confirm **Python/FastAPI** for backend services (vs TypeScript/NestJS). | FastAPI |
| Q2 | Screenshot encryption: server-side KMS envelope encryption (manager & AI can view) or true end-to-end (neither can)? | KMS envelope — required for manager gallery and AI summaries |
| Q3 | Billing: manual plan assignment for MVP, Stripe in Phase 3 — acceptable? | Yes |
| Q4 | **Clarified**: a tenant has many users (confirmed). One *account* belongs to one tenant, and emails are globally unique. Is that sufficient, or do consultants need one login across tenants (requires a workspace selector and identity redesign)? | One account per tenant |
| Q5 | Should Google login auto-provision users by verified domain, or only via invitation? | Invitation-first; domain auto-join only if the tenant enables it |
| Q6 | Primary MVP desktop platform: Windows only, or Windows + macOS at launch? | Windows first, macOS immediately after |
| Q7 | Chat in Phase 2 as documented, or pull a minimal channel into MVP? | Phase 2 |
| Q8 | Default screenshot interval and privacy window — propose 5–10 min random, 24 h deletion window. | As proposed |
| Q9 | Repository names/org: `github.com/neatsprint/*` as listed in `REPOSITORIES.md`? | As listed |
| Q10 | Do you want a public roadmap / issue tracker mirrored in GitHub Projects? | Yes, from M0 |

---

## 13. Change Control

- Scope changes require an entry in `docs/DECISIONS.md` and a MASTER_PLAN change note.
- Anything not listed in §3.1 is out of MVP by default (the "icebox" rule).
- After MVP beta begins, only bug fixes and security patches may enter the release branch.

---

**End of Scope**
