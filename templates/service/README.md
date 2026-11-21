# neatsprint-__SERVICE__

NeatSprint **__TITLE__**.

| Item | Value |
| :--- | :--- |
| Service name | `__SERVICE__` |
| Container port | `8000` |
| Host port (dev) | `__PORT__` |
| Gateway prefix | `/api/v1/__SERVICE__` |
| Database | `db___SERVICE__` |
| Owner | OpenCade (AI) / Laksiri (approval) |

## Responsibilities

See `../../docs/ARCHITECTURE.md` §3.3 for the authoritative boundary. This service owns its
logical database and must never read another service's tables.

## Run locally

```bash
uv sync
cp .env.example .env
uv run uvicorn __PACKAGE__.main:app --reload --port 8000
```

Or from the orchestrator: `docker compose up -d __SERVICE__`.

## Endpoints

| Method | Path | Purpose |
| :--- | :--- | :--- |
| GET | `/healthz` | Liveness (no dependencies) |
| GET | `/readyz` | Readiness (database check) |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/v1/ping` | Skeleton echo |

Domain endpoints are added per `docs/DEVELOPMENT_PLAN.md`.

## Test

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

## Standards

- Tenant scoping: every tenant-owned query filters `tenant_id` (docs/SECURITY.md).
- Errors: raise `neatsprint_lib.errors.ApiError`; never hand-build error JSON.
- Logs: JSON via `neatsprint_lib.logging`; no PII, tokens or screenshot content.
- Contracts: publish OpenAPI to `neatsprint-contracts` when an endpoint changes.
