# NeatSprint Runbooks

Operational procedures for the local/staging stack. Production commands assume Kubernetes and
the release image tags from `docs/DEVOPS.md`. Every alert in
`infra/observability/alerts.yml` links to a section here.

---

## Start / stop

```bash
docker compose up -d --build        # local stack
docker compose down                 # stop, keep volumes
docker compose down -v              # DESTROYS local data; re-seed afterwards
make seed                           # restore demo tenant and users
```

Health: `GET /healthz`, `GET /readyz`, `/metrics` on every service. Gateway at `:8000`, web at
`:3000`, Traefik dashboard at `:8089`.

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

## Certificate expiry

The local stack is HTTP. Production terminates TLS at the ingress/ACME; alert on
`probe_ssl_earliest_cert_expiry` and renew 30 days before expiry.
