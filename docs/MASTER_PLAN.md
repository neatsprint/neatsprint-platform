# NeatSprint — Master Plan

> **Status**: Approved v1.0 · **Version**: 1.0 · **Last updated**: 2026-11-21
> **Owner**: Laksiri Fernando · **Author**: OpenCade (AI)
> **Supersedes**: `documents/step2-mvp-roadmap.md` (kept as reference)
> **Detail level**: This is the *portfolio* view. Task-level execution lives in
> `DEVELOPMENT_PLAN.md`; verification lives in `TEST_PLAN.md`.

---

## 1. Mission & Definition of Success

**Mission**: Ship a trustworthy, privacy-honest agile delivery platform that a small team can
run in a browser and on their desktops, and that an enterprise can buy without a compliance
exception.

**Definition of success for MVP (v1.0)**:

1. Tenants can onboard, plan, execute and report on a sprint without leaving the product.
2. Desktop tracking survives four hours offline and loses nothing.
3. Screenshot deletion is real, immediate and provably irreversible — the flagship trust feature.
4. Tenant isolation and RBAC are enforced by tests, not by convention.
5. A new developer can run the whole stack locally in under 30 minutes.

---

## 2. Guiding Constraints

| Constraint | Impact on plan |
| :--- | :--- |
| Two-person effective team (human owner + AI) | Strict sequencing; no parallel horizontal layer builds; vertical slices only |
| Multi-repo with submodules | Contract-first APIs; versioned releases; no shared mutable code |
| No dedicated DevOps staff | Docker Compose for MVP, minimal k8s manifests only when needed |
| Compliance claims must be defensible | Security and privacy work is scheduled, not deferred |
| AGPLv3 open core | No dependency with incompatible licensing; legal docs before launch |

---

## 3. Phase Model

| Phase | Name | Theme | Exit gate |
| :--- | :--- | :--- | :--- |
| **M0** | Foundations | Repos, orchestration, contracts, CI skeleton | Clean `docker compose up`, CI green, contracts published |
| **M1** | Identity & Tenancy | Who you are, which tenant, what you may do | Invite → login → permission-enforced API, tested |
| **M2** | Work Management | Projects, backlog, sprints, teams | A team can plan and run a sprint end-to-end |
| **M3** | Time & Monitoring | Timer, screenshots, privacy, offline agent | 4-hour offline session syncs losslessly; deletion verified |
| **M4** | Insight & Console | Reports, dashboards, admin, UX polish | All MVP screens complete; metrics reconcile |
| **M5** | Hardening & Launch | Security, performance, docs, legal, release | MVP acceptance criteria (§8 of SCOPE) all met |
| **P2** | Collaboration | Chat, notifications, mobile, integrations | Team chat + mobile beta in production |
| **P3** | Intelligence | AI assistant, summaries, enterprise compliance | AI features GA behind enterprise plan |

M0–M5 = MVP. P2 and P3 are planned but **not started** during MVP hardening.

---

## 4. Workstreams

Each workstream has a lead (owner of decisions) and an executor. On this project the AI is the
executor for all streams; Laksiri approves gates and provides accounts/credentials.

| ID | Workstream | Scope | Gate owner |
| :--- | :--- | :--- | :--- |
| WS1 | Product & Scope | Scope, requirements, acceptance criteria, prioritisation | Laksiri |
| WS2 | Architecture | Service boundaries, contracts, data model, ADRs | Laksiri (approve) / AI (author) |
| WS3 | Platform & DevOps | Repos, compose, gateway, CI/CD, observability, backups | AI |
| WS4 | Backend services | IAM, core, task, team, worklog, monitoring, reports | AI |
| WS5 | Clients | Web, desktop agent, mobile (P2) | AI |
| WS6 | Quality | Test strategy, automation, performance, security testing | AI |
| WS7 | Security & Privacy | Threat model, controls, privacy window, audits, compliance | Laksiri (approve) / AI (author) |
| WS8 | UX & Design system | Screens, flows, tokens, copy, accessibility | AI (decides), Laksiri (reviews) |
| WS9 | Release & Operations | Environments, release process, runbooks, support | AI |

---

## 5. Milestones & Deliverables

Legend: `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked

### M0 — Foundations

**Goal**: every future commit lands in a working, tested skeleton.

- [x] Repositories created by Laksiri per `docs/REPOSITORIES.md` (15 new + this orchestrator)
- [x] Submodules added under `services/` and pinned
- [x] `neatsprint-contracts` published: OpenAPI bootstrap + shared error model
- [x] Orchestrator `docker-compose.yml`: gateway, postgres, redis, minio, mailpit, 10 services
- [x] Traefik routing for `/api/v1/*` with ForwardAuth stub
- [x] Service template: FastAPI + health endpoints + structured logging + pytest harness
- [x] Shared Python libraries: config, logging, auth middleware, DB session, outbox
  *(all delivered by M1; see `neatsprint-lib` v0.3.0)*
- [x] Web app skeleton: Next.js, design tokens, layout, auth placeholder
- [x] CI workflow template for services and clients (lint, test, build, scan)
- [x] Root `Makefile`/scripts: `bootstrap`, `migrate`, `seed`, `test`, `lint`, `down`
- [x] `.env.example` complete and documented
- [x] ADR-001…004, 007–009, 013, 014 accepted in `docs/DECISIONS.md` (005/006/010 confirmed before M3)
- [ ] Demo seed: 1 tenant, 6 users, 2 teams, 2 projects, 1 sprint, 20 items *(moved to M1)*

**Exit gate**: `docker compose up -d` on a clean machine yields a green `/healthz` for every
service, a rendering web shell and CI passing on an empty PR. Seeded demo data moves to M1 with
the first schema.

### M1 — Identity & Tenancy

**Goal**: a real person can be invited, log in, and be correctly authorised.

- [x] IAM: user model, credentials (Argon2id), sessions, refresh rotation
- [x] IAM: invitations (create, accept, revoke, expire)
- [x] IAM: Google OAuth2/OIDC login
- [x] IAM: RBAC model (roles, permissions, role_permissions, user_roles)
- [x] IAM: JWT issuance (RS256) + JWKS endpoint + revocation
- [x] IAM: password reset, deactivation, profile
- [x] IAM: audit log (append-only) + admin queries
- [x] Core: tenant provisioning, plans, settings
- [x] Core: application registry + tenant application enablement
- [x] Core: plan-limit enforcement helper + tenant settings API
- [x] Gateway: ForwardAuth, rate limits, security headers, CORS
- [x] Web: login, invitation acceptance, password reset, tenant switcher-free session shell
- [x] Web: admin — users list, invite, role assignment, deactivation
- [x] Tests: RBAC matrix, tenant isolation suite, auth E2E

**Exit gate**: invitation → registration → login → admin grants a role → member sees exactly the
permitted menu and receives `403` on everything else (verified by automated test).
*Current state: invitation → registration → login → tenant access → role enforcement, password
reset, sessions, seat limits, outbox, Google ID-token login, invitation resend, custom roles and
admin settings are verified. The only open item is the database-level tenant guard (T04, moved
to M2 for PostgreSQL RLS).*

### M2 — Work Management

**Goal**: a team can plan, run and close a sprint.

- [x] Task service: projects, project teams, backlog items, ranking, history, comments
- [x] Task service: sprint lifecycle (plan/start/complete), carry-over
- [x] Task service: attachments to object storage (presigned)
- [x] Team service: teams, members, leads, project mapping
- [x] Cross-service validation: user existence, team membership, project access
- [x] Web: projects list/create/settings
- [x] Web: backlog table with inline edit, filters, bulk actions
- [x] Web: Kanban board with drag-and-drop and optimistic updates
- [x] Web: sprint planning, sprint board, sprint completion dialog
- [x] Web: item detail drawer — description, comments, history, time summary placeholder
- [x] Web: teams admin
- [x] Notifications: in-app assignment bell with persistent read state; digest-safe email template
- [~] Tests: lifecycle, ranking concurrency, contract and component tests in place; the full
  per-screen permission matrix is tracked in M5 security hardening

**Exit gate**: create project → add items → plan sprint → move items across the board → complete
sprint with carry-over, all permission-correct. *(met; exercised in the M2 integration passes)*

### M3 — Time Tracking, Monitoring & Desktop Agent

**Goal**: the trust story becomes real.

- [x] Worklog: server-authoritative timer, sessions, manual entries, timesheets
- [x] Worklog: idempotent sync endpoint + conflict handling
- [x] Monitoring: device registration (key pair), sessions, heartbeat
- [x] Monitoring: screenshot upload (KMS envelope encryption), pending/visible states
- [x] Monitoring: privacy window enforcement, deletion pipeline, tombstones, audit
- [x] Monitoring: retention job (hard delete blobs + metadata; AI embeddings arrive with the AI service)
- [ ] Desktop: Tauri shell, tray, login, device registration, timer, idle detection
- [ ] Desktop: capture engine (multi-monitor, DPI), encryption, local queue
- [ ] Desktop: review tray (view/delete), transparency log
- [ ] Desktop: sync engine (push/pull, backoff, conflict resolution), updater
- [x] Web: my screenshots gallery, deletion flow, personal transparency log
- [x] Web: manager monitoring gallery (tombstones), session detail
- [~] Tests: backend/web round-trips, encryption and deletion verified live; the four-hour offline
  and device-control scenarios still require a real desktop build

**Exit gate**: the four-hour offline scenario and the deletion-irreversibility scenario pass on a
real desktop build, evidenced by test artefacts. *(blocked on the desktop agent and Rust/Tauri
toolchain; backend and web privacy pipeline already verified)*

### M4 — Reports, Dashboards & Console Polish

**Goal**: managers get answers; the product feels finished.

- [x] Reports: read-model database and projectors (events/outbox)
- [x] Reports: time by project/user, completion, velocity, burndown, monitoring summary
- [x] Reports: personal transparency report
- [x] Reports: CSV export and async PDF exports with signed URLs and job status
- [x] Web: dashboard with role-aware widgets
- [x] Web: reports screens with filters, charts, empty/loading/error states
- [x] Web: export centre with job status and signed downloads
- [ ] Web: settings (tenant, monitoring policy, retention, aggregation mode) — moved to M5
- [x] Web: audit log viewer
- [x] Web: responsive pass (mobile nav, table scrolling, reduced padding)
- [x] Web: accessibility audit with automated axe component suite, skip link and chart data tables
- [ ] Mobile (stretch, only if M0–M4 on schedule): read-only shell

**Exit gate**: report totals reconcile to the second with raw entries; every MVP screen matches
`UI_UX_DESIGN.md`; accessibility audit passes AA.

### M5 — Hardening & Launch

**Goal**: defensible release.

- [x] Threat model reviewed; mitigations verified
- [~] OWASP ASVS L2 checklist: self-assessment published; high gaps tracked
- [ ] Performance test at target scale; bottlenecks fixed
- [~] Backup + restore runbook documented; rehearsal pending
- [~] Observability: alerts and runbook live; Grafana per-service panels pending
- [x] Legal drafts: ToS, privacy policy, DPA, sub-processor list, monitoring disclosure
- [~] Security headers, CSP and rate limits live; dependency/container scan gate pending
- [ ] Release pipeline: signed images, versioned release, rollback procedure
- [~] Docs: README and release notes updated; API reference/onboarding dry run pending
- [ ] UAT script executed with Laksiri; acceptance criteria signed
- [ ] v1.0.0 tagged

**Exit gate**: SCOPE §8 acceptance criteria satisfied and recorded in `docs/RELEASE_NOTES.md`.

### P2 — Collaboration (post-MVP)

- [ ] Chat service: channels, messages, read state, WebSocket gateway
- [ ] Presence from desktop heartbeat, client-type icons
- [ ] Daily scrum flow
- [ ] Notification service: in-app, email, push tokens
- [ ] Mobile app: auth, assigned work, status updates, manual time, chat, push
- [ ] GitHub integration: commit/PR linking

**P2 kickoff checklist**

- [ ] Finalize chat schema and channel/team binding ADR
- [ ] Add chat/presence/notification event contracts
- [ ] Extract notification service and push token registry
- [ ] Scaffold Expo mobile with auth, assigned work and offline queue
- [ ] Add GitHub commit/PR linking with least-privilege tokens
- [ ] Carry desktop T22–T36 into P2 planning with a Rust/Tauri toolchain owner
- [ ] Close M5 open items before v1.0.0 (virus scan, shared lockout, SBOM gate, UAT, legal review)
- [ ] Saved views and command palette (if not delivered in M4)

### P3 — Intelligence (post-MVP)

- [ ] AI service scaffolding, provider adapter, prompt registry
- [ ] RAG over permitted project data (pgvector)
- [ ] Work summaries and standup drafts
- [ ] Backlog assistant with confirmation-gated writes
- [ ] Voice push-to-talk
- [ ] Custom role builder UI, legal hold, SIEM export
- [ ] Stripe billing, Gmail integration

---

## 6. Delivery Sequence (critical path)

```text
M0 Foundations
   └─ M1 IAM + Core ──┬─ M2 Task + Team ──┬─ M3 Worklog + Monitoring + Desktop
                      │                    └─ M4 Reports
                      └─ Web shell (parallel within M1/M2, same milestone)
                                            └─ M5 Hardening ── v1.0.0
```

Rules:

- **Contract before code**: the OpenAPI fragment for a service is merged before its
  implementation, so clients can build against a stable shape.
- **Vertical slice**: each milestone ends with a demoable user journey, not a layer.
- **No milestone skipping**: M3 depends on M2 item identity and M1 identity.

---

## 7. Estimated Effort

Indicative, in AI-agent working sessions (≈ 1 session = a focused delivery block). Human review
time is separate.

| Milestone             | Sessions (low) | Sessions (high) | Confidence             |
| :-------------------- | -------------: | --------------: | :--------------------- |
| M0 Foundations        |              4 |               6 | High                   |
| M1 Identity & Tenancy |              8 |              12 | Medium                 |
| M2 Work Management    |              8 |              12 | Medium                 |
| M3 Time & Monitoring  |             12 |              18 | Low (desktop + crypto) |
| M4 Reports & Console  |              7 |              10 | Medium                 |
| M5 Hardening & Launch |              6 |               9 | Medium                 |
| **MVP total**         |         **45** |          **67** |                        |
| P2 Collaboration      |             14 |              20 | Low                    |
| P3 Intelligence       |             12 |              18 | Low                    |

The widest uncertainty is M3 (desktop capture, encryption, offline sync) — it is scheduled early
enough to absorb surprises without moving the launch gate.

---

## 8. Quality Gates

Every milestone must pass **all** gates before the next begins.

| Gate | Criteria |
| :--- | :--- |
| G1 Build | All repos build from clean checkout; images build; compose starts |
| G2 Test | Unit + integration green; coverage ≥ 80% on domain logic; no skipped P0 tests |
| G3 Security | Secret scan clean; dependency scan no high/critical; authz tests green |
| G4 Contract | OpenAPI/event schemas valid, versioned, published; breaking changes recorded |
| G5 Docs | Plan checkboxes updated; ADRs recorded; README/runbook current |
| G6 Review | Laksiri reviews the milestone demo and signs the gate in `conversation.md` |

---

## 9. Risk Register

Likelihood (L) and impact (I): H/M/L. Owner is accountable for the mitigation.

| ID | Risk | L | I | Mitigation | Owner |
| :--- | :--- | :--- | :--- | :--- | :--- |
| R-01 | Desktop capture/offline complexity overruns | H | H | Build M3 spike first; Windows-first; keep macOS/Linux behind a feature flag | AI |
| R-02 | Privacy feature mis-implemented (blob survives) | M | H | Deletion pipeline tested with storage inspection; tombstone test in CI; manual adversarial review | AI |
| R-03 | Cross-tenant leakage | M | H | Repository-level tenant scoping helper, mandatory isolation tests, code review checklist | AI |
| R-04 | Microservice sprawl slows delivery | H | M | Strict service template, shared libraries, outbox, no per-service bespoke infra | Laksiri |
| R-05 | Multi-repo overhead (15 components + orchestrator) | H | M | CI templates, scripted releases, contract repo; consider merging thin services if overhead dominates | Laksiri |
| R-06 | Scope creep during MVP | M | M | Icebox rule; scope change requires DECISIONS entry | Laksiri |
| R-07 | Legal/compliance gaps block launch | M | H | Legal draft in M4, not M5; monitoring disclosure template early | Laksiri |
| R-08 | Single-region data loss | L | H | Managed Postgres with PITR, nightly logical dump to object storage, restore drill | AI |
| R-09 | LLM cost/latency (P3) | M | M | Provider adapter, caching, per-tenant quotas, streaming | AI |
| R-10 | Key management compromise (KMS) | L | H | Least-privilege KMS policies, key rotation, access audit, no keys on disk | AI |
| R-11 | Browser/OS capture permissions (macOS TCC) | M | M | Onboarding permission wizard, clear diagnostics, support runbook | AI |
| R-12 | Team bandwidth (one human reviewer) | M | M | Milestone-sized review requests, async decision log, defaults documented | Laksiri |

---

## 10. Decision Log (summary)

Full records in `docs/DECISIONS.md`.

| ADR | Decision | Status |
| :--- | :--- | :--- |
| 001 | Backend = Python 3.12 + FastAPI | Accepted |
| 002 | Database-per-service (logical DBs on one cluster for MVP) | Accepted |
| 003 | Gateway = Traefik v3 with ForwardAuth | Accepted |
| 004 | UUIDv7 client-generated identifiers | Accepted |
| 005 | Screenshot encryption = KMS envelope, not E2E | Accepted |
| 006 | Privacy window enforced server-side with pending state | Accepted |
| 007 | Services verify JWTs via JWKS (defence in depth) | Accepted |
| 008 | Reporting via read-model projections, not cross-DB joins | Accepted |
| 009 | Redis Streams + outbox for events in MVP | Accepted |
| 010 | Device binding via key pair + signed request (DPoP-style) | Accepted |
| 011 | Chat deferred to Phase 2 | Accepted |
| 012 | Many users per tenant; account belongs to one tenant (global unique email) | Accepted |
| 013 | Multi-repo with submodules and a contracts repo | Accepted |
| 014 | Next.js App Router + Tailwind + shadcn/ui for web | Accepted |
| 015 | Manual billing in MVP, Stripe in Phase 3 | Accepted |
| 016 | Screenshot blobs excluded from backups | Accepted |
| 017 | Monotonic time + server clamp for durations | Accepted |
| 018 | Runtime policy: Python services, Rust for CPU-bound, Next.js not a backend | Accepted |

---

## 11. Documentation Map

| Document | Purpose | Status |
| :--- | :--- | :--- |
| `docs/README.md` | Index and documentation conventions | Done |
| `docs/SCOPE.md` | Requirements, boundaries, acceptance | Approved |
| `docs/MASTER_PLAN.md` | This plan | Approved |
| `docs/DEVELOPMENT_PLAN.md` | Task backlog with checkboxes | Approved |
| `docs/TEST_PLAN.md` | Test strategy, suites, cases | Approved |
| `docs/ARCHITECTURE.md` | System, services, flows, deployment | Approved |
| `docs/DATA_MODEL.md` | Schemas, keys, indexes, migrations | Approved |
| `docs/API_SPEC.md` | Conventions and endpoint catalogue | Approved |
| `docs/SECURITY.md` | Threat model, controls, privacy, compliance | Approved |
| `docs/UI_UX_DESIGN.md` | Screens, design system, copy | Approved |
| `docs/DEVOPS.md` | Environments, CI/CD, observability, backups | Approved |
| `docs/REPOSITORIES.md` | Repo creation and submodule plan | Approved |
| `docs/DECISIONS.md` | ADRs | Approved |
| `docs/GLOSSARY.md` | Shared vocabulary | Done |
| `docs/CONTRIBUTING.md` | Working conventions | Done |
| `docs/SETUP_GUIDE.md` | Operator setup: local, Google, CAPTCHA, GitHub | Done |
| `docs/RUNBOOKS.md` | Operational procedures | M5 |
| `docs/CHANGELOG.md` | Delivered changes | Living |
| `docs/RELEASE_NOTES.md` | Version history | M5 |

---

## 12. Governance & Cadence

| Ritual | When | Output |
| :--- | :--- | :--- |
| Task pickup | Each `attend` message | AI message: plan + assumptions |
| Milestone demo | End of each milestone | Evidence pack (tests, screenshots), gate sign-off |
| Decision review | As needed | ADR entry + scope note |
| Risk review | End of each milestone | Updated register in §9 |
| Doc reconciliation | End of each milestone | Checkbox + doc diffs |
| Commit discipline | Every task | Conventional Commit, pushed |

**Checklist update protocol**: `[ ]` → `[~]` when started, `[x]` only with evidence. A milestone
line in §5 is ticked only when its exit gate passes.

---

## 13. Next Actions (this planning cycle)

1. Laksiri reviews `SCOPE.md` (especially §12 open questions), `REPOSITORIES.md`, and the
   milestone sequence.
2. Laksiri creates the 16 GitHub repositories and adds remotes; AI adds them as submodules.
3. AI executes **M0** as the first development task.
4. AI scaffolds the service template and one reference service (IAM) as the pattern for the rest.
5. Gate G6 review after M0.

---

**End of Master Plan**
