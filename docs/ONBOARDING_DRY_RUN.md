# Onboarding Dry Run — 2026-11-24

Scope: fresh `git clone --recurse-submodules` into an empty directory, empty Docker volumes,
`./scripts/bootstrap.ps1`, demo seed and web smoke. The host already had Docker Desktop and warm
image layers, so this is a clean-checkout rehearsal, not a blank-machine install.

## Procedure

```powershell
git clone --recurse-submodules https://github.com/neatsprint/neatsprint-platform.git $env:TEMP\neatsprint-dry
cd $env:TEMP\neatsprint-dry
# isolate volumes during the rehearsal
(Get-Content .env.example) -replace 'COMPOSE_PROJECT_NAME=neatsprint','COMPOSE_PROJECT_NAME=neatsprint-dry' | Set-Content .env
./scripts/bootstrap.ps1
```

## Result

- All nine services reported healthy on the first pass.
- Seed created the tenant, six roles, six demo users, team `Backend Squad`, project `AUTH`,
  5 backlog items and an active `Sprint 1`.
- Web login `200`; `/projects`, `/reports`, `/timesheet`, `/teams`, `/monitor`,
  `/me/screenshots`, `/admin/users`, `/admin/settings` all returned `200`.
- Rehearsal volumes were removed afterwards; the development stack was restored from its own
  preserved volumes.

## Finding and fix

**CRLF shell scripts broke every backend on Windows.** A fresh clone checked out
`docker/entrypoint.sh` with CRLF (`core.autocrlf=true`), so the container failed with
`exec /app/docker/entrypoint.sh: no such file or directory`. IAM, Core, Task, Team, Worklog,
Monitoring and Reports all restarted in a loop; Chat/AI stayed up because they have no entrypoint.

Fixed by adding `*.sh text eol=lf` to `.gitattributes` in each affected service (IAM via PR #7)
and the orchestrator. A second fresh clone produced an LF entrypoint and the full bootstrap passed.

## Documentation fixes

- README now lists the demo accounts and password, `bootstrap`/manual setup, reset commands and
  optional observability/ClamAV profiles.
- Corrected the web stack description to Next.js 16 and the web package manager to npm.
- Removed the stale "until M1 lands" note.

## Residual & Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-ONB-01**: Re-run the clean-clone onboarding procedure on a blank VM (no pre-cached
  Docker layers) to measure cold-start download and build time against the 30-minute target
  (`MASTER_PLAN.md` §1 #5).
- [ ] **IMP-ONB-02**: Have `scripts/bootstrap.ps1` and `scripts/bootstrap.sh` check for host port
  conflicts (`8000`, `3000`, `5432`, `6379`, `9000`, `9090`) up front and print the owning PID and
  the `.env` override variable before invoking `docker compose up`.
