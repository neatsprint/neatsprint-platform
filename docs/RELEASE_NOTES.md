# Release Notes

## v1.0.5 — 2026-11-26

> Web-only patch for the intermittent sign-in navigation race.

### Fixed

- Sign-in and sign-out now use a hard browser navigation (`window.location.assign`) instead of
  `router.push()` followed immediately by `router.refresh()`. The previous combination could cancel
  the pending App Router navigation, leaving the login form visible until the user refreshed.
- Verified three consecutive sign-out → prefilled sign-in cycles in the browser, each landing on
  `/admin/users` without a manual refresh.
- Google Identity Services stylesheet is now allowed by CSP (`style-src`), removing the last GSI
  CSP console error on the login page.

## v1.0.4 — 2026-11-26

> Build-only patch. Restores a green release gate after a new Debian `libzstd1` advisory.

### Fixed

- Python runtime images now run `apt-get upgrade -y` before installing `git`/`ca-certificates`, so
  `libzstd1` and other refreshed Debian packages are included. The v1.0.3 release workflow failed
  only on `CVE-2026-124851` in `neatsprint-chat`; the rebuilt image rescans clean.

## v1.0.3 — 2026-11-26

> Security and UX patch following the post-v1.0.2 review. No schema-breaking changes.

### Fixed

- **Reports tenant isolation (`IMP-T01`)**: `GET /reports/burndown` now rejects a foreign tenant's
  `sprint_id` with `404` instead of leaking sprint dates. Task now emits `item.deleted` and Reports
  removes the projection so soft-deleted items disappear from completion and velocity figures.
- **Database RLS (`IMP-T02`)**: tenant-bound request sessions and PostgreSQL RLS policies were added
  for Reports, Worklog, Monitoring, Core tenant settings/applications and IAM
  sessions/roles/invitations/audit/notifications. Auth-critical tables keep their global-email
  lookup path.
- **Web navigation & permissions (`IMP-T03`)**: the Reports sidebar link is enabled; `MEMBER` users
  can create backlog items (`task:item:create`); Board/Backlog/Planning expose the Settings tab; the
  topbar timer reflects a running session.
- **CSP (`IMP-T04`)**: Google Identity Services script/style and the local staging ports are now
  allowed, removing the login-page CSP errors.
- **Reports SQL (`IMP-T05`, SQL part)**: completion, velocity, burndown and monitoring reports now
  aggregate in PostgreSQL instead of loading every fact into Python.

### Verified

- IAM/Core/Task/Reports/Worklog/Monitoring: ruff, mypy and pytest green.
- Web: typecheck, 22 tests and production build pass.
- Live smoke: login `200`; projects, teams, reports, timesheet, monitoring, IAM users and tenant
  settings `200`; 1 MiB screenshot upload 47 ms warm.

## v1.0.2 — 2026-11-24

> Patch release. Team membership UI and a page-rendering fix.

### Fixed

- **Team members**: the Teams page now lists members and lets users with `team:member:manage`
  add an active user as Member or Lead, or remove a member. New BFF routes proxy the Team API.
- **Header identity**: the app shell shows the signed-in user's name/initials and a **Sign out**
  action; it no longer shows a misleading “Sign in” link while authenticated.
- **Stuck “Loading…” pages**: removed the route-level `loading.tsx` skeletons that left Projects,
  Teams, Timesheet, Reports, Monitoring and the project pages on their fallback under the
  Next 16 production streaming path. Content now renders directly.
- Verified end to end: team add `201`, page shows the member, remove `204`; 22 web tests,
  typecheck and production build pass.

## v1.0.1 — 2026-11-24

> Patch release. Adds the missing backlog create flow.

### Fixed

- **Backlog create UI**: the web backlog now has a **New item** drawer (title, type, priority,
  estimate, description) and a BFF `POST /api/session/projects/{id}/backlog` route. Permission is
  enforced by the API; viewers still receive `403`.
- Verified end to end: owner create `201`, item visible in the backlog, delete `204`; viewer
  create `403 permission_denied`; 21 web tests, typecheck and production build pass.

## v1.0.0 — 2026-11-24

> Status: **released 2026-11-24** — UAT signed off with a desktop waiver under ADR-019.
> Date: 2026-11-24.

### Highlights

- Multi-tenant identity, RBAC, invitations, sessions and tenant settings.
- Projects, backlog, board, sprint planning, teams and project access enforcement.
- Timer, manual time, offline sync, timesheets and CSV/PDF exports.
- Encrypted screenshots with a privacy window, deletion tombstones, audit and transparency log.
- Assignment notifications and a digest-safe email template.
- Reports, dashboards, saved views, global search, command palette and admin audit viewer.
- Hardening: cross-tenant probe, security headers, resource limits, alerts, runbooks and legal
  drafts.

### Known limitations

- **Desktop agent (Tauri/Rust) is deferred** under ADR-019: offline capture, SQLCipher, signed
  updater and installer evidence are not available in this release candidate. UAT item 4 is
  blocked and needs an explicit waiver or a follow-up milestone.
- PDF exports render directly with ReportLab rather than an HTML-to-PDF headless render.
- Legal counsel review and the 72-hour post-launch window are still pending.
- Base images use mutable tags; rebuild and re-run the Trivy gate at each release.

### Upgrade notes

- New migrations: IAM notifications/audit, Task saved views, Worklog/Monitoring initial schemas,
  Reports read models/exports.
- Set `MONITORING_ENCRYPTION_KEY` before first monitoring use; changing it requires rewrapping
  existing data keys.
- Run `python scripts/seed.py` after a volume reset.

### Verification

- Cross-tenant probe: 8/8 PASS on local staging.
- Unit/integration: IAM 27, Task 31, Worklog 10, Monitoring 10, Reports 9, Web 20; all services
  and Lib green.
- Load: 100 tenants / 5,157 users / 1M entries; 0% errors, read p95 267 ms, write p95 77 ms.
- Screenshot upload: 1 MiB accepted in 38 ms warm; EICAR rejected with `422 malware_detected`.
- Supply chain: Trivy 0 high/critical across 10 images; gitleaks clean across 70 commits.
- Staging smoke and clean-clone bootstrap: pass.
- Builds: all services, web production build.
