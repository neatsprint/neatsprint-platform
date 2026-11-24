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

## Follow-ups

- Automate nightly encrypted dumps and retention in the staging environment.
- Add a restore verification job that checks row counts and one login before declaring success.
- Rehearse a point-in-time recovery on staging before v1.0.0.
