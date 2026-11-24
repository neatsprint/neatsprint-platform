# UAT Script — v1.0.0

Owner: Laksiri Fernando · Prepared: 2026-11-24 · Status: **awaiting execution**

Record pass/fail and evidence for each SCOPE §8 item. Do not tag `v1.0.0` until all items are
PASS or an explicit waiver is recorded.

| # | Acceptance item | Steps | Expected | Result | Evidence |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | Tenant provisioning + invite | Provision a tenant, seed owner, invite `member@` and accept | Login and member visible | ☐ | |
| 2 | Permission matrix | For each role, call a denied and an allowed route | Denied = 403/404; allowed = 200 | ☐ | |
| 3 | Tenant isolation | Run `python scripts/security/cross_tenant_probe.py` | All checks PASS | ☐ | |
| 4 | 4-hour offline desktop | Desktop agent offline, timer + captures, reconnect | Zero loss/duplicates | ☐ **blocked (desktop deferred)** | |
| 5 | Screenshot deletion | Upload capture, delete in window, check blob/manager | Blob gone, tombstone visible | ☐ | |
| 6 | Report reconciliation | Compare `/reports/time` with raw entries | Totals match to the second | ☐ | |
| 7 | Backup restore | Follow `docs/BACKUP_REHEARSAL.md` | Restore verified | ☐ | |
| 8 | Load test | Run k6 at NFR-PERF targets | Error rate < 0.1% | ☐ **pre-verified** | `docs/LOAD_TEST.md`: 0% errors, read p95 267 ms |
| 9 | ASVS L2 | Review `docs/ASVS_L2.md` | No open high/critical | ☐ **pre-verified** | Desktop item deferred (ADR-019) |
| 10 | Clean-machine quick start | Clone, `./scripts/bootstrap.ps1`, login | Works on a clean machine | ☐ **pre-verified** | `docs/ONBOARDING_DRY_RUN.md` |

## Pre-UAT evidence (2026-11-24)

- **Tenant isolation (#3)**: `scripts/security/cross_tenant_probe.py` — 8/8 PASS.
- **Load (#8)**: 100 tenants / 5,157 users / 1M entries; 0% errors, read p95 267 ms,
  write p95 77 ms; 1 MiB screenshot upload 38 ms warm. See `docs/LOAD_TEST.md`.
- **ASVS (#9)**: high gaps closed except desktop verification, deferred by ADR-019.
  Secret scan, SBOM and container scan are clean. See `docs/ASVS_L2.md` and `docs/SBOM.md`.
- **Quick start (#10)**: fresh clone + empty volumes + bootstrap + seed + web smoke passed.
  See `docs/ONBOARDING_DRY_RUN.md`.
- **Backup (#7)**: `docs/BACKUP_REHEARSAL.md` records the last restore.

These are pre-checks; record the UAT-session result and evidence in the table above.

## Sign-off

- Product owner: ____________________ Date: ________
- Engineering: ______________________ Date: ________
- Notes/waivers:
