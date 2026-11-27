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

Patch: **v1.0.1** (backlog create), **v1.0.2** (team members, header identity, page-rendering
fix) and **v1.0.3** (reports isolation, RLS, navigation/CSP, SQL reports) deployed to local
staging on 2026-11-24/26; the 72-hour window continues from the v1.0.0 start.

## Daily check (record one line per day)

```powershell
docker compose --env-file .env.staging ps --format "{{.Service}} {{.State}} {{.Health}}"
$env:BASE_URL="http://localhost:8100/api/v1"; $env:WEB_URL="http://localhost:3100";
$env:SMOKE_PASSWORD="NeatSprint!2026"; python scripts/smoke/staging_smoke.py
```

- Day 1 (2026-11-25): 15/15 services running, 0 restarts, 0 tracebacks, no 5xx in the gateway
  log. Backfilled on 2026-11-27 from container state and logs; the smoke script was not run that
  day.
- Day 2 (2026-11-26): 15/15 running after the v1.0.3 redeploy (08:54 IST); 2× `502` on
  `POST /api/v1/auth/login` between 03:23:44Z and 03:24:29Z while IAM restarted, recovered
  automatically; 0 restarts and 0 tracebacks after the redeploy. Smoke not run that day.
- Day 3 (2026-11-27, 20:43 IST): 15/15 running and healthy; gateway `/ping` 200, web `/login` 200;
  staging smoke 7/7 pass (ping, login, projects, timesheet, teams, reports, web); 0 restarts
  across the stack for the whole window; 0 tracebacks; total 5xx over 72 h = the 2 redeploy 502s
  above. Note: the staging images predate the unreleased sprint-selection, CSV `sprint_id` and
  timesheet hydration fixes (web image built 2026-11-26 06:38Z), so those three changes were not
  exercised by this window.

Also review the RED dashboard (`docker compose --env-file .env.staging --profile observability up -d`,
Grafana `:3201`) and `infra/observability/alerts.yml`. Record any 5xx burst, p95 regression or
firing alert, with the response taken.

## Close-out

T26 closes when the three daily lines are recorded and no unresolved P0/P1 issue remains. Open a
follow-up task for anything deferred (desktop agent, legal review).
