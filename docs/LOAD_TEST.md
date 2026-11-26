# Load Test — Target Volume

Date: 2026-11-24 · Tool: k6 (Docker) · Script: `scripts/load/api-mix.js` ·
Seed: `scripts/load/seed_volume.sql`

## Data volume

| Entity | Target | Seeded |
| :--- | ---: | ---: |
| Tenants | 100 | **100** |
| Users | 5,000 | **5,157** |
| Work-log entries | 1,000,000 | **1,000,003** |
| Report time facts | 1,000,000 | **1,000,009** |

98 synthetic tenants, 250 users in the demo tenant (plus 4,900 across the others) and 1M time
entries spread over Nov 2026–Feb 2027. Reports were queried over the default 30-day window, which
covers ~200k facts.

## Result — API mix

10 VUs, 50 seconds, five demo users, 15% backlog writes.

| Metric | NFR target | Observed |
| :--- | :--- | :--- |
| Error rate | < 0.1% | **0.00%** (0 / 1,743) |
| Read p95 (all) | < 300 ms | **267 ms** |
| Read p50 | — | 19 ms |
| Write p95 | < 500 ms | **77 ms** |
| Throughput | — | ~33 req/s |

Per endpoint p95: projects 40 ms, backlog 98 ms, timesheet 32 ms, teams 29 ms, reports 465 ms.
The reports endpoint has its own NFR (`< 5 s` cached, `< 30 s` cold) and is comfortably inside it;
excluding reports, read p95 is under 100 ms.

## Result — screenshot upload

`scripts/load/screenshot_upload.py`: 5 × 1 MiB PNG through login → work session → device →
monitoring session → encrypted upload (ClamAV enabled).

| Metric | NFR target | Observed |
| :--- | :--- | :--- |
| First upload | < 2 s (1 MiB, 10 Mbps) | **233 ms** |
| Warm p50 | < 2 s | **38 ms** |
| Warm p95 | < 2 s | **233 ms** |

Loopback is faster than a 10 Mbps link, so this proves the server-side path, not the network
budget. A 1 MiB payload at 10 Mbps needs ~800 ms of transfer alone, still inside 2 s.

## Bottleneck fixed

The first target-volume run failed read p95 at **4.4 s**. `/reports/time` loaded every fact row
into Python and aggregated in a loop (~200k ORM objects per request). The endpoint now does
`GROUP BY` / `SUM` in PostgreSQL; cold response dropped to **84–180 ms**, and the full mix passes.
The 30-second in-process report cache can stampede once it expires, which is why report p95 under
sustained load sits around 465 ms.

## Reproduce

```bash
# 1. seed target volume (tenant/project ids from the running demo)
Get-Content -Raw scripts/load/seed_volume.sql | docker compose exec -T postgres psql -U neatsprint \
  -d db_core -v tenant=<tenant-uuid> -v project=<project-uuid> -f -

# 2. API mix
Get-Content scripts/load/api-mix.js | docker run --rm -i grafana/k6 run -

# 3. screenshot path
python scripts/load/screenshot_upload.py
```

## Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-PRF-01 (Move remaining report endpoints to SQL & Redis cache)**: Rewrite
  `completion_report`, `velocity_report`, `burndown_report` and `monitoring_report` in
  `neatsprint-reports` to aggregate in PostgreSQL (`GROUP BY`/`SUM`) and back `services/cache.py`
  with Redis + single-flight locking to eliminate the 30 s cache-expiry stampede (`IMP-T05`).
- [ ] **IMP-PRF-02 (Web LCP benchmark — `NFR-PERF-04`)**: Run Lighthouse against the production
  web build on a throttled profile to verify LCP < 2.5 s (`TC-PERF-005`).
- [ ] **IMP-PRF-03 (Async report export benchmark at 250-person scale)**: Benchmark cold CSV/PDF
  export generation (`POST /reports/exports`) at 250-user / 1M-entry volume (< 30 s target).
- [ ] **IMP-PRF-04 (Cleanup script for target-volume seed)**: Add `scripts/load/cleanup_volume.sql`
  to remove synthetic `load-tenant-*` / `loaduser-*` / `load-entry-*` rows without requiring a full
  `docker compose down -v`.

The synthetic rows live only in the local database. Reset with `docker compose down -v` and
re-run `./scripts/bootstrap.ps1` before a demo or UAT.
