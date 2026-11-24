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
| 8 | Load test | Run k6 at NFR-PERF targets | Error rate < 0.1% | ☐ **pending** | |
| 9 | ASVS L2 | Review `docs/ASVS_L2.md` | No open high/critical | ☐ | |
| 10 | Clean-machine quick start | Clone, `docker compose up -d --build`, `make seed`, login | Works on a clean machine | ☐ | |

## Sign-off

- Product owner: ____________________ Date: ________
- Engineering: ______________________ Date: ________
- Notes/waivers:
