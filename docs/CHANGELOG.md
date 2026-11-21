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

- 2026-11-21 — Reset the reference roadmap's misleading pre-ticked MVP items; progress now lives
  in `docs/MASTER_PLAN.md` and `docs/DEVELOPMENT_PLAN.md`.

---

## Release History

| Version | Date | Notes |
| :--- | :--- | :--- |
| — | — | No releases yet. `v1.0.0` is the MVP release (milestone M5). |
