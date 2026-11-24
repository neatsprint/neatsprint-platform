# Post-Launch Health Window — v1.0.0

Start: **2026-11-24 19:12 +05:30** (tag `v1.0.0`, release run `45406253483`, success)
End: **2026-11-27 19:12 +05:30** (72 hours)

Environment: local staging profile (`neatsprint-staging`, web `:3100`, API `:8100`).
Every image in the release matrix built and passed the Trivy gate.

## Baseline (2026-11-24 19:16 +05:30)

| Check | Result |
| :--- | :--- |
| Release workflow | success — 10/10 images, SBOM + Trivy |
| Staging services | 10/10 running and healthy |
| Gateway `/ping` | 200 |
| Staging smoke | pass (ping, login, projects, timesheet, teams, reports, web) |
| UAT | 9/10 pass, desktop waived via ADR-019 |
| Cross-tenant probe | 8/8 pass |

## Daily check (record one line per day)

```powershell
docker compose --env-file .env.staging ps --format "{{.Service}} {{.State}} {{.Health}}"
$env:BASE_URL="http://localhost:8100/api/v1"; $env:WEB_URL="http://localhost:3100";
$env:SMOKE_PASSWORD="NeatSprint!2026"; python scripts/smoke/staging_smoke.py
```

- Day 1 (2026-11-25):
- Day 2 (2026-11-26):
- Day 3 (2026-11-27):

Also review the RED dashboard (`docker compose --env-file .env.staging --profile observability up -d`,
Grafana `:3201`) and `infra/observability/alerts.yml`. Record any 5xx burst, p95 regression or
firing alert, with the response taken.

## Close-out

T26 closes when the three daily lines are recorded and no unresolved P0/P1 issue remains. Open a
follow-up task for anything deferred (desktop agent, legal review).
