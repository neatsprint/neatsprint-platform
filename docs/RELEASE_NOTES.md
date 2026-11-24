# Release Notes

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
