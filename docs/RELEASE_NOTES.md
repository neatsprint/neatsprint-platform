# Release Notes — v1.0.0 (release candidate)

> Status: **draft for UAT/sign-off**. Do not tag `v1.0.0` until Laksiri signs the acceptance
> checklist. Date: 2026-11-24.

## Highlights

- Multi-tenant identity, RBAC, invitations, sessions and tenant settings.
- Projects, backlog, board, sprint planning, teams and project access enforcement.
- Timer, manual time, offline sync, timesheets and CSV/PDF exports.
- Encrypted screenshots with a privacy window, deletion tombstones, audit and transparency log.
- Assignment notifications and a digest-safe email template.
- Reports, dashboards, saved views, global search, command palette and admin audit viewer.
- Hardening: cross-tenant probe, security headers, resource limits, alerts, runbooks and legal
  drafts.

## Known limitations

- **Desktop agent (Tauri/Rust) is deferred** under ADR-019: offline capture, SQLCipher, signed
  updater and installer evidence are not available in this release candidate.
- Upload virus scanning, shared brute-force lockout and a zero-high/critical supply-chain gate are
  still open M5 items.
- PDF exports render directly with ReportLab rather than an HTML-to-PDF headless render.
- UAT, legal counsel review and the 72-hour post-launch window are pending.

## Upgrade notes

- New migrations: IAM notifications/audit, Task saved views, Worklog/Monitoring initial schemas,
  Reports read models/exports.
- Set `MONITORING_ENCRYPTION_KEY` before first monitoring use; changing it requires rewrapping
  existing data keys.
- Run `python scripts/seed.py` after a volume reset.

## Verification

- Cross-tenant probe: PASS (`scripts/security/cross_tenant_probe.py`).
- Unit/integration: IAM 27, Task 31, Worklog 10, Monitoring 10, Reports 9, Web 20.
- Builds: all services, web production build.
