# NeatSprint Runbooks

> **Status**: Skeleton (expanded in M5) · **Last updated**: 2026-11-21
> **Owner**: OpenCade (AI)

Operational procedures. Each entry follows: **symptom → impact → action → verify → follow-up**.
Commands assume the repository root unless stated.

---

## RB-01 — Start the local stack

**Symptom**: need a working environment.

```bash
./scripts/bootstrap.ps1      # Windows
./scripts/bootstrap.sh       # macOS/Linux
```

**Verify**: `docker compose ps` shows every service healthy; <http://localhost:8000/ping> returns 200.

---

## RB-02 — Stop or reset the stack

```bash
docker compose down          # stop, keep data
docker compose down -v       # stop and delete local volumes (destroys data)
```

**Follow-up**: after `-v`, run bootstrap again; databases are recreated from
`infra/postgres/init/01-databases.sql`.

---

## RB-03 — A service is unhealthy

```bash
docker compose ps
docker compose logs --tail=200 <service>
curl -s http://localhost:<port>/healthz
curl -s http://localhost:<port>/readyz
```

Readiness failing usually means Postgres is down or the database does not exist. Check
`docker compose logs postgres` and the logical databases.

---

## RB-04 — Rebuild one service after a dependency change

```bash
docker compose build --no-cache <service>
docker compose up -d <service>
```

---

## RB-05 — Rotate local JWT keys (from M1)

1. Generate a new RSA key pair; keep the previous public key in JWKS during overlap.
2. Update the secret/env for IAM.
3. Restart IAM; verify `/readyz`.
4. Confirm tokens issued before rotation still validate until expiry.

---

## RB-06 — Restore a database (from M5)

1. Provision a clean database.
2. Restore the latest verified backup.
3. Run migrations to head.
4. Verify row counts and run the smoke suite.
5. Record actual RTO in `docs/RELEASE_NOTES.md`.

> Screenshot blobs are intentionally excluded from backups (ADR-016). Never attempt to
> restore deleted screenshot content.

---

## RB-07 — Privacy deletion failed (S1)

**Symptom**: a deleted screenshot still returns content, or a blob remains.

1. Disable the monitoring module for the tenant (`PUT /core/tenant-applications/MONITORING`).
2. Delete the object directly from storage by key; delete its wrapped key.
3. Purge `ai_embeddings`/`ai_documents` rows for the source.
4. Verify `screenshots.state = DELETED`, `storage_key IS NULL`.
5. Write an incident record; notify the tenant admin within 24 h.
6. Add a regression test mirroring the failure before closing.

---

## RB-08 — Suspected cross-tenant access (S1)

1. Revoke the involved sessions/devices.
2. Freeze the affected service deployment (scale to 0 if data is actively leaking).
3. Collect request ids, tenant ids and audit rows.
4. Patch, add an isolation test, deploy through the hotfix path.
5. Follow `SECURITY.md` §13 notification timeline.

---

## RB-09 — Gateway returns 502/503

```bash
docker compose logs gateway
docker compose ps
```

Traefik resolves services by container DNS name. A 502 means the target container is down,
still starting, or on a different network. Confirm the service name matches
`services/neatsprint-apigw/dynamic/services.yml`.

---

## RB-10 — Disk pressure from screenshots (from M3)

1. Confirm retention settings for the tenant.
2. Run the retention job manually; verify deletion audit rows.
3. Reduce the default retention only with tenant notice — it is a privacy commitment.

---

**Add a runbook when you add an alert.** An alert without a procedure is not merged.
