# NeatSprint — DevOps & Operations Plan

> **Status**: Approved v1.0 · **Version**: 1.0 · **Last updated**: 2026-11-21
> **Owner**: Laksiri Fernando · **Author**: OpenCade (AI)
> **Supersedes**: `documents/step5-deployment-and-cicd-architecture.md`
> **Related**: `REPOSITORIES.md`, `ARCHITECTURE.md` §13–14, `SECURITY.md` §13–14

---

## 1. Environments

| Environment | Purpose | Infra | Data | Access |
| :--- | :--- | :--- | :--- | :--- |
| **local** | Development | Docker Compose on a laptop | Seeded demo | Developer |
| **ci** | Automated verification | Ephemeral containers per job | Factories | CI only |
| **staging** | Pre-release, UAT, demos | Single-node k8s or compose on a VM, managed Postgres | Synthetic + anonymised | Team |
| **production** | Customers | Managed Postgres/Redis/S3 + k8s, Traefik ingress | Real | Break-glass only |

Promotion path: `feature branch → main → image → staging → tag → production`.
Nothing is deployed to production by a human running commands on a server.

### 1.1 Local stack (Docker Compose)

```text
traefik        :8000 (http), :8089 (dashboard)
web            :3000
iam            :8001   core :8002   task :8003   team :8004
worklog        :8005   monitor :8006   chat :8007   reports :8008   ai :8009
postgres       :5432 (single cluster, logical DBs)
redis          :6379
minio          :9000 (api) / :9001 (console)
mailpit        :8025 (ui) / :1025 (smtp)
```

Optional profile `observability`: prometheus `9090`, grafana `3001`, loki `3100`, promtail.
Optional profile `chaos`: toxiproxy for latency/failure testing.

Rules:

- The object-storage bucket (`neatsprint`) is created automatically by the MinIO image on first
  start via `MINIO_DEFAULT_BUCKETS`; there is no init container.
- `docker compose up -d` must work on a clean machine with only `.env` from `.env.example`.
- Services wait on `depends_on` healthchecks; migrations run via a one-shot `migrate` service.
- Volumes are named and resettable with `make clean`.
- No service mounts source code in production-like profiles; dev uses bind mounts for hot reload.

### 1.2 Configuration

- 12-factor: all configuration via environment variables, validated at boot by
  `pydantic-settings`. The app fails fast with a readable error listing missing keys.
- `.env.example` is the contract and is kept current; a CI check diffs env keys used in code
  against the example.
- Secrets are never in `.env` for shared environments; local dev uses obviously fake values.

---

## 2. CI/CD

### 2.1 Repository pipelines

Each repository has its own workflow; templates live in `neatsprint-platform/.github/workflows`
and are copied (or referenced as reusable workflows) so improvements propagate.

**Backend service pipeline**

```text
lint (ruff) ─┐
types (mypy) ─┼─► unit tests ─► integration tests (pg+redis+minio) ─► contract tests
secrets ─────┘                                                    ─► docker build
                                                                  ─► trivy scan
                                                                  ─► sbom (syft)
                                                                  ─► sign (cosign) on main
                                                                  ─► push GHCR (:sha, :latest)
```

**Web pipeline**

```text
install (pnpm, cache) → lint → tsc → vitest → playwright (chromium) → axe
→ next build → image → trivy → push
```

**Desktop pipeline**

```text
rustfmt + clippy → cargo test → tauri build (windows) → sign (dev) → artifact
nightly: tauri build (macos) + smoke
```

### 2.2 Pipeline rules

| Rule | Reason |
| :--- | :--- |
| Total PR pipeline < 12 min target | Keep the loop fast |
| Integration tests use containers, not shared DBs | Determinism |
| Coverage gate fails below threshold for changed code | Prevent drift |
| Secrets scanned on every push and PR | Leak prevention |
| Images tagged with `sha-<short>` and semver; `latest` never used in prod | Traceability |
| Builds are reproducible: lockfiles + pinned base image digests | Supply chain |
| Migrations validated on a copy of staging schema | Avoid deploy surprises |

### 2.3 Branch protection

- `main`: require PR, 1 review (Laksiri or AI self-review checklist for agent-authored PRs),
  status checks, linear history, no force-push.
- Service repos: same, plus required "contract" check.
- Orchestrator: submodule pins must reference pushed commits (CI verifies).

### 2.4 Release flow

```text
1. All milestone tasks done; gate tests green.
2. Bump versions (semver) per service; update CHANGELOG.
3. Tag each service repo (vX.Y.Z); images built and signed.
4. Orchestrator: bump submodule pins; tag platform (vX.Y.Z).
5. Deploy to staging automatically from the platform tag; run smoke + E2E.
6. Promote to production with an explicit approval (GitHub Environment).
7. Post-deploy: verify health, error rate, latency for 30 min.
8. Rollback: redeploy previous image tag (migrations are expand/contract safe).
```

Versioning: **SemVer** for services and clients; the platform version is the product version
(`1.0.0` = MVP).

---

## 3. Container Standards

- Multi-stage builds; runtime image `python:3.12-slim` (or `distroless` where practical).
- Non-root user (`uid 10001`), read-only root filesystem, `tmpfs` for `/tmp`.
- No shell tools in runtime images; healthcheck via the app's `/healthz`.
- `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`, pinned hashes in `uv.lock`.
- Image labels: `org.opencontainers.image.source`, `.revision`, `.version`, `.created`.
- Size target: services < 200 MB, web < 250 MB.
- One process per container. Workers (report export, retention) are separate deployments using
  the same image with a different command.

---

## 4. Kubernetes (staging → production)

MVP production may run on a single managed k8s cluster; manifests are intentionally simple.

```text
namespace: neatsprint-prod
  deployment/<service>        replicas 2, HPA on CPU/RPS
  service/<service>           ClusterIP :8000
  ingress/traefik             TLS, security headers, rate limits
  cronjob/retention           daily screenshot + audit retention
  cronjob/report-export       worker pool (or deployment consumer)
  job/migrate-<service>       pre-deploy hook (Helm)
  secret/ from CSI            DB, redis, KMS, SMTP, JWT keys
```

Standards:

- `resources.requests/limits` on every container.
- `readinessProbe: /readyz`, `livenessProbe: /healthz`, `startupProbe` for slow boot.
- `PodDisruptionBudget` for customer-facing services.
- `topologySpreadConstraints` across nodes where available.
- NetworkPolicy: services accept traffic only from the gateway and named peers.
- No `latest` tags; image digest pinned by Argo/Helm values.

GitOps: Helm charts in `neatsprint-infra`, Argo CD syncs staging automatically and production on
approval. Argo is introduced at M5; before that, a scripted deploy to a single VM is acceptable.

---

## 5. Observability

### 5.1 Signals

| Signal | Implementation |
| :--- | :--- |
| Logs | Structured JSON to stdout → Promtail → Loki; 30-day retention |
| Metrics | Prometheus scrape `/metrics`; service RED metrics + business metrics |
| Traces | OpenTelemetry SDK → Collector → Tempo (or Jaeger); 10% sampling, 100% on errors |
| Errors | Sentry-compatible (web, desktop opt-in, services) |
| Audit | Postgres append-only, separate from observability |

### 5.2 Required metrics per service

- `http_requests_total{route,method,status}`
- `http_request_duration_seconds` histogram
- `db_pool_in_use`, `db_query_duration_seconds`
- `outbox_pending`, `stream_consumer_lag`
- Domain: `active_timers`, `screenshots_pending`, `screenshots_deleted_total`,
  `report_export_jobs{state}`, `sync_batch_rejected_total`

### 5.3 SLOs (MVP)

| SLI | Target | Alert |
| :--- | :--- | :--- |
| API availability | 99.9% monthly | 5xx > 1% for 5 min |
| API latency p95 | < 300 ms read / < 500 ms write | p95 > 2× target for 10 min |
| Login success rate | > 99% (excluding invalid credentials) | drop > 2% over 15 min |
| Screenshot upload success | > 99.5% | > 3 failures/min for 10 min |
| Sync processing lag | < 60 s p95 | lag > 5 min |
| Report job success | > 99% | 2 consecutive failures |

### 5.4 Dashboards

1. **Platform overview** — request rate, error rate, p95, saturation, active tenants.
2. **Per-service RED** — for each service.
3. **Business** — active timers, hours tracked, captures, deletions, sprint throughput.
4. **Data** — DB connections, slow queries, partition sizes, outbox/stream lag.
5. **Security** — 401/403 rates, cross-tenant attempts, deletion anomalies, KMS errors.

### 5.5 Alert routing

- Severity P1 (outage, data loss, breach) → page immediately.
- P2 (degraded, backlog) → business-hours channel.
- P3 (disk trending, certificate expiry) → ticket.
- Every alert links to a runbook section; an alert without a runbook is not merged.

---

## 6. Backup, Restore & Disaster Recovery

| Asset | Method | Frequency | Retention | RPO/RTO |
| :--- | :--- | :--- | :--- | :--- |
| Postgres | Managed automated backups + PITR | continuous WAL, daily snapshot | 30 days | 15 min / 4 h |
| Postgres (logical) | `pg_dump` to object storage | nightly | 30 days | 24 h / 8 h |
| Object storage (uploads, exports) | Versioning + cross-region copy (prod) | continuous | 30 days | 15 min / 4 h |
| Screenshot blobs | **not backed up** (privacy decision) | — | — | — |
| Secrets | Vault/secret manager backup | daily | 30 days | 1 h / 4 h |
| Config/IaC | Git | continuous | forever | minutes |

Restore drill (quarterly, and before release):

1. Provision a clean database from the latest snapshot.
2. Run migrations to the current version.
3. Verify row counts, latest timestamps, and a sample of cross-service references.
4. Run the smoke suite against the restored environment.
5. Record actual RTO and any manual steps in `docs/RUNBOOKS.md`.

---

## 7. Security Operations

- **Access**: SSO to cloud/GitHub; no shared accounts; least-privilege roles; quarterly review.
- **Secrets**: managed store; CSI mount; rotation calendar; no `.env` on servers.
- **Images**: signed, scanned, pinned; admission policy rejects unsigned images (production).
- **Network**: private subnets for data; services not internet-facing; egress allow-list for LLM,
  SMTP, object storage.
- **Patching**: weekly dependency PRs; monthly host/node patch window; emergency path documented.
- **Audit**: cloud audit logs retained 1 year; platform audit log retained per policy.
- **Incident**: see `SECURITY.md` §13; contact tree maintained in `docs/RUNBOOKS.md`.

---

## 8. Cost & Capacity (MVP guidance)

| Item | Sizing (MVP) | Notes |
| :--- | :--- | :--- |
| Kubernetes | 3 × 2 vCPU / 4 GB nodes | Room for 2 replicas per service |
| Postgres | 2 vCPU / 4 GB, 100 GB SSD | Single cluster, logical DBs |
| Redis | 1 GB | Cache, rate limits, streams |
| Object storage | 100 GB + growth | Screenshots dominate; retention bounds it |
| LLM (P3) | usage-based | Per-tenant quotas and alerts |
| Monitoring | 30-day logs, 90-day metrics | Adjust after baseline |

Cost guards: screenshot retention default 30 days, weekly partitioning, report caching, AI quotas.

---

## 9. Runbook Index (content owned by M5)

| Runbook | When |
| :--- | :--- |
| Start / stop / restart the stack | Development, staging |
| Rotate JWT signing keys | Quarterly or suspected compromise |
| Rotate database credentials | Quarterly or incident |
| Restore database from backup | Data loss, corruption |
| Revoke all sessions / a device | Security incident |
| Disable a module tenant-wide | Feature failure or abuse |
| Drain and redeploy a service | Bad release |
| Handle a failed migration | Deploy failure |
| Respond to a privacy deletion failure | S1 incident |
| Investigate a cross-tenant report | S1 incident |
| Certificate renewal | 30 days before expiry |
| Scale up for a demo / load test | Planned event |

Each runbook: symptom, impact, immediate action, verification, communication, follow-up.

---

## 10. Definition of Operationally Ready

Before a service is considered production-ready:

- [x] Health and readiness endpoints implemented and probed
- [x] Metrics exported and dashboarded
- [x] Structured logs with request/trace ids, no PII
- [x] Alerts defined with runbook links
- [x] Resource requests/limits set
- [x] Migrations run as a pre-deploy job and are expand/contract safe
- [x] Backup/restore implications documented
- [x] Graceful shutdown (drain connections, finish in-flight requests)
- [x] Timeouts and retries configured on all outbound calls
- [x] Rate limits and quotas applied where relevant
- [x] Runbook section written

---

## 11. Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-OPS-01 (Web pipeline & package manager alignment — §2.1)**: Update §2.1 to specify
  `npm ci` (with `package-lock.json`) and Next.js 16.4.6 rather than `pnpm`.
- [ ] **IMP-OPS-02 (Container hardening & digest pinning — §2.2, §3)**:
  1. Pin base image digests (`python:3.12-slim@sha256:...`, `node:22-alpine@sha256:...`) so rebuilds
     are bit-reproducible (`SBOM.md`).
  2. Add `read_only: true` with `tmpfs: [/tmp]` on stateless service containers in Compose/Helm (§3).
  3. Add `cosign` keyless image signing to `.github/workflows/release.yml` (§2.1).
- [ ] **IMP-OPS-03 (ClamAV volume & reload resilience)**: Persist `/var/lib/clamav` in a named
  volume so virus definitions survive container recreation, and add an auto-restart/watchdog hook if
  `clamd` stalls during its initial `freshclam` reload (`RUNBOOKS.md`).
- [ ] **IMP-OPS-04 (Makefile completeness)**: Add `migrate`, `seed` and `staging` targets to the
  root `Makefile` (`IMP-T09`).
- [ ] **IMP-OPS-05 (Loki / Promtail & OpenTelemetry Collector profiles)**: Wire Loki + Promtail and
  an OTel Collector into the `observability` Compose profile (currently only Prometheus and Grafana
  are defined in `docker-compose.yml`).

---

**End of DevOps Plan**
