# Backup & Restore Rehearsal

Date: 2026-11-24 · Environment: local Docker Compose · Operator: OpenCade

## Procedure executed

```bash
docker compose exec -T postgres pg_dump -U neatsprint -Fc -f /tmp/db_task.dump db_task
docker compose exec -T postgres createdb -U neatsprint db_task_restore
docker compose exec -T postgres pg_restore -U neatsprint -d db_task_restore /tmp/db_task.dump
# same for db_iam
```

## Results

| Database | Restored rows | Result |
| :--- | :--- | :--- |
| `db_task` | 3 projects, 6 backlog items | PASS |
| `db_iam` | 7 users, 51 audit rows | PASS |

- Scratch databases were dropped after verification.
- Wall-clock duration was under 15 seconds for both dumps and restores on the local volume.
- Screenshot blobs are intentionally excluded from backups.

## RTO / RPO

- **RPO**: 24 hours (nightly dumps).
- **RTO**: 2 hours for production (restore, verify, switch traffic). Local rehearsal is not a
  production timing benchmark.

## Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-BKP-01**: Automate nightly encrypted `pg_dump` backups across all nine logical
  databases (`db_iam`…`db_ai`) with 14-day retention in the staging/production environment.
- [ ] **IMP-BKP-02**: Add a scripted restore verification job that checks row counts, cross-service
  ID integrity, and one authenticated login before declaring success.
- [ ] **IMP-BKP-03**: Rehearse PostgreSQL point-in-time recovery (PITR) on managed Postgres before
  onboarding external production tenants.
