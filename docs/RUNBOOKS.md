# NeatSprint Runbooks

Operational procedures for the local/staging stack. Production commands assume Kubernetes and
the release image tags from `docs/DEVOPS.md`. Every alert in
`infra/observability/alerts.yml` links to a section here.

---

## Environment lifecycle (dev and staging)

Two isolated Compose projects can run side by side:

| Environment | Project | Web | API | Env file | Entry point |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Development | `neatsprint` | `:3000` | `:8000` | `.env` | `./scripts/bootstrap.ps1` |
| Local staging | `neatsprint-staging` | `:3100` | `:8100` | `.env.staging` | `./scripts/staging.ps1` |

Run every command from the repository root.

### Development

```powershell
# first start, or after a clone/volume reset (creates .env, builds, waits, seeds)
./scripts/bootstrap.ps1

# normal up; keeps existing volumes and data
docker compose up -d

# rebuild only what changed, then restart it
docker compose up -d --build neatsprint-task neatsprint-web

# include ClamAV (also set CLAMAV_HOST=clamav in .env so Task/Monitoring use it)
docker compose --profile security up -d --build

# include ClamAV and observability
docker compose --profile "*" up -d --build

# status and logs
docker compose ps
docker compose logs -f --tail=100 <service>

# stop containers but keep them, the network and all volumes
docker compose --profile "*" stop

# remove containers and the network, keep named volumes (data survives)
docker compose --profile "*" down

# DESTRUCTIVE: removes volumes and all local data; re-run bootstrap/seed afterwards
docker compose --profile "*" down -v

# idempotent demo data
python scripts/seed.py
```

Plain `docker compose down` only removes services in active profiles. `clamav` (profile
`security`) and Prometheus/Grafana (profile `observability`) stay up unless you pass
`--profile "*"`. That is why a bare `down` can appear to leave containers behind.

### Local staging

```powershell
# build, start, seed and run the smoke check
./scripts/staging.ps1

# start without rebuilding
./scripts/staging.ps1 -NoBuild

# DESTRUCTIVE: stop the staging project and delete its volumes
./scripts/staging.ps1 -Down

# manual equivalents
docker compose --env-file .env.staging --profile "*" up -d --build
docker compose --env-file .env.staging --profile "*" stop
docker compose --env-file .env.staging --profile "*" down
docker compose --env-file .env.staging ps
```

Staging has its own network (`neatsprint-staging`), volumes and ports, so it does not touch
development data. `.env.staging` is git-ignored; it is created from `.env.staging.example` on the
first run.

### Stop everything without losing data

```powershell
docker compose --profile "*" stop
docker compose --env-file .env.staging --profile "*" stop
```

Restart everything with the matching `--profile "*" up -d` commands. Never add `-v` to a
stop/down command unless you intend to destroy PostgreSQL, MinIO and Redis data for that
environment.

### Refresh base images

`--build` alone reuses cached base layers. To pick up refreshed bases and rebuild:

```powershell
docker compose --profile "*" build --pull
docker compose --profile "*" up -d
```

For a fully clean rebuild: `docker compose --profile "*" build --no-cache --pull` before `up -d`.

Health after any change: `GET /healthz`, `GET /readyz`, `/metrics` on every service. Dev gateway
`:8000`, dev web `:3000`, Traefik dashboard `:8089`; staging gateway `:8100`, web `:3100`,
Traefik dashboard `:8189`.

### Port already in use

Compose fails before starting a service when a host port is taken, for example
`bind: Only one usage of each socket address ... :9090`. Find the owner and either stop it or
move NeatSprint:

```powershell
Get-NetTCPConnection -LocalPort 9090 -State Listen | Select-Object OwningProcess
Get-Process -Id <pid>
```

If the owner is unrelated software, change the matching variable in `.env` (or `.env.staging`):
`PROMETHEUS_PORT`, `GRAFANA_PORT`, `GATEWAY_HTTP_PORT`, `POSTGRES_PORT`, `WEB_PORT`, and so on.
Then rerun `docker compose up -d`. Do not stop host services you do not own.

## Service down

1. `docker compose ps` and `docker compose logs --tail=100 <service>`.
2. Check dependencies: Postgres (`pg_isready`), Redis (`redis-cli ping`), MinIO health.
3. Restart one service: `docker compose up -d <service>`.
4. If the database is unavailable, restore from backup (below) before restarting writers.
5. Confirm `/readyz` is `200` and the gateway route returns a normal response.

## High error rate

1. Identify the service from the alert labels and check `/metrics` for status classes.
2. Inspect structured logs; `request_id` is present on every problem response.
3. If a deploy caused it, roll back the image tag and re-run the smoke suite.
4. If a dependency is failing, check its health and recent latency before restarting.

## High latency

1. Check Postgres slow queries and connection counts.
2. Check Redis latency and stream consumer lag.
3. Confirm report/export jobs are not saturating CPU or MinIO.
4. Scale the affected service or reduce export concurrency.

## Gateway 5xx

1. Check Traefik logs and `traefik_service_requests_total` by service.
2. Verify ForwardAuth/IAM is reachable; a JWKS outage causes 5xx on protected routes.
3. Confirm upstream health; a 502 usually means the container is down or restarting.

## Database backup and restore

Backups are nightly `pg_dump` per logical database, encrypted at rest, retained 14 days.

```bash
# backup
docker compose exec -T postgres pg_dump -U neatsprint -Fc db_task > db_task.dump
# restore into a scratch database first
docker compose exec -T postgres createdb -U neatsprint db_task_restore
docker compose exec -T postgres pg_restore -U neatsprint -d db_task_restore < db_task.dump
```

RTO target 2 h, RPO 24 h (MVP). Validate row counts and a login before switching traffic.
Screenshot blobs are deliberately excluded from backups.

## Screenshot deletion incident

1. Verify the row is `DELETED` and `storage_key IS NULL`.
2. Confirm the object is absent from the bucket and the `deletion_audit` row exists.
3. Check `screenshot_views` for unexpected manager access.
4. If a blob survives, delete it manually, record the incident and open a P1.

## Secret and key rotation

1. JWT signing keys rotate every 90 days with overlapping JWKS (`infra/keys` locally, KMS in
   production).
2. Rotate `MONITORING_ENCRYPTION_KEY` only with a migration plan: existing objects need the old
   key to decrypt. Rewrap data keys before removing the old key.
3. Rotate `BOOTSTRAP_TOKEN` after bootstrap/seed operations and restart services.
4. Rotate Postgres, MinIO and SMTP credentials in the secret manager; never in git.
5. Re-run the cross-tenant probe and smoke suite after rotation.

## Incident and on-call

- Severity: P1 data exposure / privacy breach; P2 outage; P3 degraded feature.
- P1: contain, preserve audit logs, notify the tenant admin within 24 h, post-incident review
  within 5 days.
- P2: acknowledge within 15 min, update every 30 min.
- Every incident gets a timeline, root cause, and a regression test or runbook update.

## Release and rollback

1. Merge to `main`; CI builds and scans images.
2. Tag `vX.Y.Z`; publish release notes and images to GHCR.
3. Deploy to staging, run smoke + cross-tenant probe, then production.
4. Rollback = redeploy the previous image tag; database migrations are forward-only, so never
   roll back a schema without a reviewed down plan.

## Outbox / event lag

1. Check Redis stream length and consumer group pending counts.
2. Confirm the relay task is running in each producing service.
3. If a consumer is stuck, restart it; processed-event and source-event idempotency make replay
   safe.
4. Reports backfill: `python -m neatsprint_reports.backfill --tenant <id>`.

## Upload malware scanning

ClamAV is optional and runs under the `security` profile:

```bash
CLAMAV_HOST=clamav docker compose --profile security up -d clamav
docker compose up -d neatsprint-task neatsprint-monitoring
```

Task and Monitoring call `clamd` INSTREAM on confirm/upload. If the scanner is configured but
unreachable, uploads fail closed with `503 dependency_unavailable`. The first start downloads the
virus database and can take several minutes; wait for the healthcheck.

If the container stays unhealthy right after the first `freshclam` update, restart it:
`docker compose restart clamav`. The database is already on disk, so it comes up in seconds.

Test with the EICAR sample in a scratch file (never commit it): the upload must return
`422 malware_detected` and the blob must be removed. Verified 2026-11-24: EICAR →
`422 malware_detected`; with `clamav` stopped → `503 dependency_unavailable` (fail closed).

## SBOM and vulnerability scan

The release workflow generates an SPDX SBOM per image and runs Trivy at HIGH/CRITICAL with
`ignore-unfixed: true`. Locally, the Docker daemon is not mounted inside the Trivy container, so
save the image and scan the archive:

```bash
docker save neatsprint-neatsprint-web:latest -o /tmp/web.tar
docker run --rm -v /tmp:/work -v trivy-cache:/root/.cache/trivy \
  aquasec/trivy:0.69.3 image --input /work/web.tar \
  --severity HIGH,CRITICAL --ignore-unfixed --scanners vuln
```

Use Trivy **0.69.3 or earlier**; v0.69.4 was compromised upstream. Pin `trivy-action` to `0.35.0`
or a safe SHA. Latest result and SBOM artefacts: `docs/SBOM.md` and `docs/sbom/`.

## Cloud staging deploy and smoke

The cloud/VPS staging environment is a single host running the Compose stack (or a single-node
k8s cluster once Helm lands), with managed PostgreSQL/Redis/S3 and no production data. For the
local staging profile beside dev, use the lifecycle section above instead.

1. Pin the release: checkout the platform tag and `git submodule update --init --recursive`.
2. Create the host env file (for example `.env.staging`) from `.env.staging.example` and set
   production secrets, `COMPOSE_PROJECT_NAME`, `NEXT_PUBLIC_API_BASE_URL`, and TLS/domain values.
   Never commit it.
3. `docker compose --env-file .env.staging pull && docker compose --env-file .env.staging up -d`
   (images come from GHCR; do not build on the VM).
4. Wait for `/ping` and every `/healthz`, then run:

```bash
BASE_URL=https://staging.example/api/v1 \
WEB_URL=https://staging.example \
SMOKE_EMAIL=smoke@example.com SMOKE_PASSWORD=... \
python scripts/smoke/staging_smoke.py
```

5. Run the Playwright critical journeys and record the result in `docs/UAT.md`.
6. Roll back by redeploying the previous image tag; migrations are expand/contract.

## Certificate expiry

The local stack is HTTP. Production terminates TLS at the ingress/ACME; alert on
`probe_ssl_earliest_cert_expiry` and renew 30 days before expiry.
