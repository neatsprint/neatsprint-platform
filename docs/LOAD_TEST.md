# Load Test — API Mix

Date: 2026-11-24 · Tool: k6 (Docker) · Script: `scripts/load/api-mix.js`

## Scope

Local Docker Compose stack, 5 demo users, 10 VUs ramping over 50 seconds, mixed reads
(projects, backlog, timesheet, reports, teams) plus 15% backlog writes. This is a **smoke load**,
not the full 100-tenant / 5,000-user target volume.

## Result

| Metric | Target | Observed |
| :--- | :--- | :--- |
| Error rate | < 0.1% | **0.00%** (0 / 2,083) |
| Read p95 | < 300 ms | **~37 ms** |
| Write p95 | < 500 ms | **~47 ms** |
| Overall p95 | — | **54 ms** |
| Throughput | — | ~41 req/s |

The first run mixed a member token into the reports read and produced 3.7% 403s; the script now
uses an owner token for report reads and passes. The gateway per-user rate limit (600/min) is the
first ceiling at higher VU counts.

## Not yet proven

- Target-scale data volume (1M work logs, 100 tenants).
- Screenshot upload throughput and 10 Mbps 1 MB acceptance.
- Report cold-query latency at 250-person tenant scale.

Follow-up: run the same script against staging with seeded volume and a higher test-user pool, and
add a separate upload scenario. Keep the rate-limit bucket in mind and use dedicated load-test
users.
