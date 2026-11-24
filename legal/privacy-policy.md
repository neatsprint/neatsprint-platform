# NeatSprint Privacy Policy

> **Draft — counsel review required before publication.** Last updated: 2026-11-24.

## Who we are

NeatSprint provides work-management and privacy-first work tracking. The controller for a hosted
workspace is the customer organisation; NeatSprint acts as processor. For our own website and
account administration we act as controller.

## What we collect

| Category | Examples | Purpose |
| :--- | :--- | :--- |
| Account | name, email, role, avatar | Authentication and collaboration |
| Work data | projects, tasks, sprints, comments, time entries | Delivering the service |
| Device data | device name, platform, public key fingerprint, last seen | Device binding and revocation |
| Monitoring data | screenshots (only while a timer runs), activity heartbeats | Disclosed work tracking |
| Audit data | logins, admin actions, screenshot views and deletions | Security and transparency |
| Billing | plan and invoice references (manual in MVP) | Contract administration |

We do not collect keystrokes, audio, camera, clipboard contents, browser history, private
messages or files.

## Monitoring rules

- Capture only while the timer is running, with a visible indicator.
- Screenshots are encrypted at ingest and visible to the user first.
- The user can delete a capture inside the configured privacy window; deletion destroys the image
  and any derived embeddings. Managers see a tombstone, never the image.
- The workspace admin chooses the interval, privacy window and retention within product limits.

## Legal bases

Performance of a contract, legitimate interests in secure service operation, consent where
required for monitoring, and legal obligations. Employment-law consultation is the customer's
responsibility.

## Sharing

We share data with the sub-processors listed in `subprocessors.md`, with the customer's
authorised users, and with authorities where legally required. We do not sell personal data.

## Retention

Account and work data follow the contract and workspace settings. Time entries are retained for
the configured statutory period. Screenshot blobs follow the workspace retention setting and are
excluded from backups; tombstones are retained for audit. Audit logs are retained for one year
hot and longer where required.

## Your rights

Access, rectification, erasure, restriction, portability and objection. Workspace users should
contact their workspace admin first; we support the admin in fulfilling requests. You may complain
to your supervisory authority.

## Security

TLS in transit, encryption at rest for screenshots, tenant isolation, least-privilege permissions,
audit logging, dependency scanning and regular backups (excluding screenshot blobs).

## Contact

**privacy@neatsprint.com** · Data Protection Officer: **[name/contact]**
