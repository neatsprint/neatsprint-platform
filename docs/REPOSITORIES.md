# NeatSprint — Repository Strategy & Submodule Plan

> **Status**: Approved v1.0 · **Version**: 1.0 · **Last updated**: 2026-11-21
> **Owner**: Laksiri Fernando · **Author**: OpenCade (AI)
> **Answers**: project brief rule 5 ("once you finalize the git repositories, let me know")

This document is the final list of repositories to create. Once they exist, the AI adds them as
git submodules under `services/` and pins them (M0-T01).

---

## 1. Topology

**Multi-repo with an orchestrator.** This repository (`neatsprint-platform`) is the orchestrator:
documentation, Compose files, gateway configuration, scripts, seeds, E2E tests and submodule pins.
It contains no product source code.

- **15 new repositories** + this orchestrator = **16 repositories**.
- Each service/client is independently versioned, built and released.
- Shared contracts (`neatsprint-contracts`) and shared libraries (`neatsprint-lib`) prevent
  duplication without creating a distributed monolith.

```text
neatsprint-platform            (this repo)
└── services/                  (git submodules)
    ├── neatsprint-contracts/
    ├── neatsprint-lib/
    ├── neatsprint-apigw/
    ├── neatsprint-iam/
    ├── neatsprint-core/
    ├── neatsprint-task/
    ├── neatsprint-team/
    ├── neatsprint-worklog/
    ├── neatsprint-monitoring/
    ├── neatsprint-chat/
    ├── neatsprint-reports/
    ├── neatsprint-ai/
    ├── neatsprint-web/
    ├── neatsprint-desktop/
    └── neatsprint-mobile/
```

---

## 2. Repository Catalogue

| # | Repository | Type | Stack | Milestone | Purpose |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | `neatsprint-platform` | Orchestrator | Compose, scripts, docs | exists | Docs, local stack, gateway wiring, E2E, seeds |
| 2 | `neatsprint-contracts` | Library | OpenAPI 3.1, JSON Schema, AsyncAPI | M0 | API/event contracts, generated types, mock server |
| 3 | `neatsprint-lib` | Library | Python 3.12 | M0 | Shared FastAPI/lib: config, logging, errors, auth, DB, outbox, UUIDv7 |
| 4 | `neatsprint-apigw` | Service | Traefik v3 config | M0 | Edge routing, ForwardAuth, rate limits, headers |
| 5 | `neatsprint-iam` | Service | FastAPI | M1 | Auth, users, roles, permissions, invitations, audit |
| 6 | `neatsprint-core` | Service | FastAPI | M1 | Tenants, plans, applications, settings |
| 7 | `neatsprint-task` | Service | FastAPI | M2 | Projects, backlog, sprints, comments, attachments |
| 8 | `neatsprint-team` | Service | FastAPI | M2 | Teams, membership, project-team mapping events |
| 9 | `neatsprint-worklog` | Service | FastAPI | M3 | Timer, time entries, timesheets, sync |
| 10 | `neatsprint-monitoring` | Service | FastAPI | M3 | Devices, screenshots, privacy window, retention |
| 11 | `neatsprint-chat` | Service | FastAPI + WS | P2 | Channels, messages, presence |
| 12 | `neatsprint-reports` | Service | FastAPI | M4 | Read-model projections, reports, exports |
| 13 | `neatsprint-ai` | Service | FastAPI + pgvector | P3 | RAG assistant, summaries, drafts |
| 14 | `neatsprint-web` | Client | Next.js 15 + TS | M0 | Web application |
| 15 | `neatsprint-desktop` | Client | Tauri v2 + Rust + React | M3 | Desktop agent |
| 16 | `neatsprint-mobile` | Client | Expo + React Native | P2 | Mobile app |

> Gate: repositories 11, 13 and 16 can be created empty at the start (README + license only) and
> implemented later. Creating them now reserves the names and keeps the submodule tree stable.

### 2.1 Why not fewer repositories?

Consolidating would reduce CI overhead, but the brief explicitly asks for separate repositories per
service/client, and independent release cadence is genuine value for the desktop agent and web app.
Mitigations for the overhead: shared CI templates, one `Makefile` in the orchestrator, contract-first
generation, and a single seed/observability stack.

### 2.2 Optional consolidation (flagged for Laksiri)

If repository overhead proves painful, the lowest-risk merges are:

1. `neatsprint-team` into `neatsprint-core` (thin service, few tables).
2. `neatsprint-apigw` into the orchestrator (configuration only).
3. `neatsprint-lib` into `neatsprint-contracts` (single "shared" repo).

None are required for v1.0. Decision: keep separate unless the master plan records a change.

---

## 3. Naming & Metadata

- GitHub org: **`neatsprint`** (or the org Laksiri prefers — confirm).
- Names are lowercase, hyphenated, prefixed `neatsprint-`.
- Visibility: **public** for `platform`, `contracts`, `lib`, services and clients (open core,
  AGPLv3); private only if a commercial component is introduced later.
- Licence: AGPLv3 (`LICENSE` copied from the platform repo) for all code repositories.
- Every repo has: `README.md` (purpose, quick start, env vars, API/CLI, status), `LICENSE`,
  `CONTRIBUTING.md` (link to platform guide), `SECURITY.md` (link), `.gitignore`, `CODEOWNERS`.
- Default branch: `main`. Topic tags: `neatsprint`, `microservice` | `frontend` | `desktop`.
- Description format: `NeatSprint <component> — <one line>`.

---

## 4. Creation Order

Create in this order so dependencies resolve.

| Step | Repository | Why now |
| :-: | :--- | :--- |
| 1 | `neatsprint-contracts` | Everything else generates from it |
| 2 | `neatsprint-lib` | Service template depends on it |
| 3 | `neatsprint-apigw` | Gateway config needed for local stack |
| 4 | `neatsprint-iam` | Reference implementation |
| 5 | `neatsprint-core` | Tenant bootstrap |
| 6 | `neatsprint-task` | First real domain service |
| 7 | `neatsprint-team` | Task depends on it |
| 8 | `neatsprint-worklog` | Tracking |
| 9 | `neatsprint-monitoring` | Privacy-critical |
| 10 | `neatsprint-reports` | Consumes events |
| 11 | `neatsprint-web` | UI against contracts |
| 12 | `neatsprint-desktop` | Agent |
| 13 | `neatsprint-chat` | Placeholder for P2 |
| 14 | `neatsprint-ai` | Placeholder for P3 |
| 15 | `neatsprint-mobile` | Placeholder for P2 |

---

## 5. Exact Commands

### 5.1 Create on GitHub (gh CLI)

Run from the platform directory. Requires `gh auth login` with org permissions.

```bash
ORG=neatsprint

for repo in contracts lib apigw iam core task team worklog monitoring reports chat ai web desktop mobile; do
  gh repo create "$ORG/neatsprint-$repo" --public \
    --description "NeatSprint $repo component" \
    --add-readme
done
```

Then, per repository:

```bash
# initialise locally (once), commit the scaffold, push
git init -b main
git add .
git commit -m "chore: initial scaffold"
git remote add origin "https://github.com/$ORG/neatsprint-<name>.git"
git push -u origin main
```

### 5.2 Register submodules in the orchestrator (AI does this in M0-T01)

```bash
git submodule add https://github.com/neatsprint/neatsprint-contracts.git services/neatsprint-contracts
git submodule add https://github.com/neatsprint/neatsprint-lib.git services/neatsprint-lib
git submodule add https://github.com/neatsprint/neatsprint-apigw.git services/neatsprint-apigw
git submodule add https://github.com/neatsprint/neatsprint-iam.git services/neatsprint-iam
git submodule add https://github.com/neatsprint/neatsprint-core.git services/neatsprint-core
git submodule add https://github.com/neatsprint/neatsprint-task.git services/neatsprint-task
git submodule add https://github.com/neatsprint/neatsprint-team.git services/neatsprint-team
git submodule add https://github.com/neatsprint/neatsprint-worklog.git services/neatsprint-worklog
git submodule add https://github.com/neatsprint/neatsprint-monitoring.git services/neatsprint-monitoring
git submodule add https://github.com/neatsprint/neatsprint-chat.git services/neatsprint-chat
git submodule add https://github.com/neatsprint/neatsprint-reports.git services/neatsprint-reports
git submodule add https://github.com/neatsprint/neatsprint-ai.git services/neatsprint-ai
git submodule add https://github.com/neatsprint/neatsprint-web.git services/neatsprint-web
git submodule add https://github.com/neatsprint/neatsprint-desktop.git services/neatsprint-desktop
git submodule add https://github.com/neatsprint/neatsprint-mobile.git services/neatsprint-mobile
git commit -m "chore(submodules): register component repositories (M0-T01)"
```

### 5.3 Daily submodule workflow

```bash
# clone everything
git clone --recurse-submodules https://github.com/neatsprint/neatsprint-platform.git
# update all to their pinned commits after a pull
git submodule update --init --recursive
# work inside a service
cd services/neatsprint-iam && git switch -c feat/login && ...
# after the service PR merges, bump the pin from the orchestrator
cd ../..
git add services/neatsprint-iam
git commit -m "chore(submodules): bump iam to v0.3.1"
```

Rules:

- Never commit inside a submodule and forget to push it — CI blocks pins to unpushed commits.
- The orchestrator pin is the integration version; staging deploys from a platform tag.
- Force-pushing a tagged service commit is forbidden.

---

## 6. Standard Repository Layout

### 6.1 Backend service

```text
neatsprint-<svc>/
├── src/
│   ├── api/            routers, dependencies, schemas (request/response)
│   ├── core/           domain logic and policies
│   ├── db/             models, repositories, session
│   ├── clients/        typed clients to other services
│   ├── events/         publishers, consumers, outbox handlers
│   ├── settings.py
│   └── main.py
├── migrations/         Alembic
├── tests/
│   ├── unit/ integration/ contract/
├── docker/
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── .env.example
├── .github/workflows/ci.yml
└── README.md
```

### 6.2 Client

```text
neatsprint-web/
├── src/app/            routes (route groups: (auth), (app))
├── src/components/     ui/ and domain/
├── src/lib/            api client, utils
├── src/hooks/
├── src/types/          generated from OpenAPI
├── public/brand/
├── e2e/                Playwright
├── package.json
└── README.md
```

---

## 7. Branch Protection & Review

| Setting | Value |
| :--- | :--- |
| Default branch | `main` |
| Require PR | yes |
| Required approvals | 1 (human for the first release; AI self-review checklist acceptable afterwards) |
| Required checks | lint, types, unit, integration, contract (`contracts` repo), secret scan |
| Require branches up to date | yes |
| Require linear history | yes (squash merge) |
| Force push / deletion | disabled |
| Signed commits | recommended, required at M5 |
| Environments | `staging` (auto), `production` (manual approval) |

Labels (in every repo): `type:feature`, `type:bug`, `type:chore`, `area:iam`, `area:task`,
`area:worklog`, `area:monitoring`, `area:reports`, `area:web`, `area:desktop`, `priority:high`,
`needs:design`, `needs:decision`, `blocked`.

---

## 8. Versioning & Release

| Component | Versioning | Tag | Artifact |
| :--- | :--- | :--- | :--- |
| Services | SemVer | `v0.x.y` → `v1.0.0` at MVP | `ghcr.io/neatsprint/<svc>:vX.Y.Z` |
| Contracts | SemVer | `vX.Y.Z` | npm package `@neatsprint/contracts`, python wheel |
| Lib | SemVer | `vX.Y.Z` | python package `neatsprint-lib` |
| Web | SemVer | `vX.Y.Z` | container image |
| Desktop | SemVer | `vX.Y.Z` | MSI/DMG, update manifest |
| Platform | SemVer (product) | `vX.Y.Z` | release notes + submodule pins |

Compatibility: services must tolerate the previous minor version of their dependencies (expand/
contract). A breaking contract change requires a major of `neatsprint-contracts` and coordinated
releases.

---

## 9. Checklist for Laksiri (repository creation)

- [ ] Confirm GitHub org name (default `neatsprint`)
- [ ] Confirm public visibility and AGPLv3 licence for all repos
- [ ] Create the 15 repositories (step 4 order)
- [ ] Add `LICENSE` and initial `README.md` to each (or let the AI scaffold after creation)
- [ ] Enable branch protection per §7
- [ ] Create GitHub Environments `staging` and `production`
- [ ] Create a registry credential for `ghcr.io` if packages are private
- [ ] **(Optional)** create a dedicated machine account for the agent; otherwise the owner's `gh`
  session is used (no AI account exists by default)
- [ ] Tell the AI "repositories created" in `agent/conversation.md`
- [ ] AI runs M0-T01 and records the pins

---

## 10. What Lives Where (quick reference)

| Concern | Home |
| :--- | :--- |
| Product docs | `neatsprint-platform/docs` |
| Original reference docs | `neatsprint-platform/documents` |
| Compose + gateway wiring | `neatsprint-platform` (+ `services/neatsprint-apigw`) |
| Seeds, E2E, scripts | `neatsprint-platform` |
| API + event schemas | `neatsprint-contracts` |
| Shared Python libraries | `neatsprint-lib` |
| UI application | `neatsprint-web` |
| Desktop agent | `neatsprint-desktop` |
| Mobile app | `neatsprint-mobile` |
| Infra/Helm/Terraform | `neatsprint-platform/infra` for MVP; may split later (ADR required) |

---

**End of Repository Strategy**
