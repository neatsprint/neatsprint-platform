# UAT Script — v1.0.0

Owner: Laksiri Fernando · Prepared: 2026-11-24 · Executed: 2026-11-24 on local staging
Status: **executed — awaiting sign-off**

Record pass/fail and evidence for each SCOPE §8 item. Do not tag `v1.0.0` until all items are
PASS or an explicit waiver is recorded.

Environment: `./scripts/staging.ps1` (project `neatsprint-staging`, web `:3100`, API `:8100`,
ClamAV enabled).

| # | Acceptance item | Steps | Expected | Result | Evidence |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | Tenant provisioning + invite | Provision a tenant, seed owner, invite `member@` and accept | Login and member visible | PASS | Invite 201, accept 201, new user login 200, owner sees user |
| 2 | Permission matrix | For each role, call a denied and an allowed route | Denied = 403/404; allowed = 200 | PASS | All roles 200 on `/tasks/projects`; admin/manager/lead/member/viewer denied 403 on their probe; owner has full tenant permissions |
| 3 | Tenant isolation | Run `python scripts/security/cross_tenant_probe.py` | All checks PASS | PASS | 8/8, including `beta timesheet via alpha` 0 rows |
| 4 | 4-hour offline desktop | Desktop agent offline, timer + captures, reconnect | Zero loss/duplicates | ☐ **blocked (desktop deferred)** | ADR-019 |
| 5 | Screenshot deletion | Upload capture, delete in window, check blob/manager | Blob gone, tombstone visible | PASS | Blob existed before, gone after; subject + manager see `DELETED`; manager content 404 |
| 6 | Report reconciliation | Compare `/reports/time` with raw entries | Totals match to the second | PASS | API 5 s = worklog 5 s = report facts 5 s |
| 7 | Backup restore | Follow `docs/BACKUP_REHEARSAL.md` | Restore verified | PASS | `pg_dump`/`pg_restore` of `db_task`; 2 projects, 6 items |
| 8 | Load test | Run k6 at NFR-PERF targets | Error rate < 0.1% | PASS | Staging 0% errors, p95 37.5 ms; target volume 0% / 267 ms in `docs/LOAD_TEST.md` |
| 9 | ASVS L2 | Review `docs/ASVS_L2.md` | No open high/critical | PASS | Only desktop verification remains, deferred by ADR-019 |
| 10 | Clean-machine quick start | Clone, `./scripts/bootstrap.ps1`, login | Works on a clean machine | PASS | `docs/ONBOARDING_DRY_RUN.md` |

## Pre-UAT evidence (2026-11-24)

- **Tenant isolation (#3)**: 8/8 PASS on staging.
- **Load (#8)**: 100 tenants / 5,157 users / 1M entries; 0% errors, read p95 267 ms,
  write p95 77 ms; 1 MiB screenshot upload 38 ms warm. See `docs/LOAD_TEST.md`.
- **ASVS (#9)**: high gaps closed except desktop verification. Secret scan, SBOM and container
  scan are clean. See `docs/ASVS_L2.md` and `docs/SBOM.md`.
- **Quick start (#10)**: fresh clone + empty volumes + bootstrap + seed + web smoke passed.
  See `docs/ONBOARDING_DRY_RUN.md`.
- **Backup (#7)**: staging dump/restore verified above; the earlier rehearsal is in
  `docs/BACKUP_REHEARSAL.md`.

Two operational findings were fixed during UAT: the seed now adds manager/lead/member to the
squad (manager tombstone visibility), and MinIO's named volume now mounts at
`/bitnami/minio/data` where the image actually stores objects.

## Sign-off

- Product owner: ____________________ Date: ________
- Engineering: ______________________ Date: ________
- Notes/waivers:
