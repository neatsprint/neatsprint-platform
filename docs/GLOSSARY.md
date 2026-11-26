# NeatSprint — Glossary

> **Status**: Living · **Last updated**: 2026-11-21

Shared vocabulary for documents, code, API fields and UI copy. Where a term appears in the UI, the
**UI label** column is the user-facing wording.

---

## 1. Tenancy & Identity

| Term | Definition | UI label |
| :--- | :--- | :--- |
| **Tenant** | An isolated organisation using NeatSprint. Billing and data-isolation boundary; contains many users. | Workspace |
| **Tenant Owner** | Human accountable for the tenant and its subscription. | Owner |
| **Application** | A module the platform can provide (e.g. Task Management, Monitoring). Global entity shared by tenants. | App |
| **Tenant application** | The enablement record linking a tenant to an application. | Module |
| **Plan** | Commercial tier that constrains users, projects and retention. | Plan |
| **User** | A person with one account in one tenant. A tenant has many users; each logs in independently. | Person / Member |
| **Role** | Named bundle of permissions, system or custom. | Role |
| **Permission** | A single capability string `domain:resource:action`. | Permission |
| **Invitation** | Time-limited token sent by email to join a tenant. | Invitation |
| **Session** | A logged-in device/token family. | Session / Signed-in device |
| **Device** | A registered installation of the desktop or mobile app, bound to a key pair. | Device |
| **Service account** | Non-human identity used between services or by the AI (`AI_AGENT`). | — |
| **Break-glass** | Audited, time-boxed operator elevation for incident response. | — |

## 2. Work Management

| Term | Definition | UI label |
| :--- | :--- | :--- |
| **Project** | Container for a body of work; has a unique key (e.g. `AUTH`). | Project |
| **Project key** | Short uppercase identifier used to build item keys. Immutable after creation. | Key |
| **Backlog** | Ordered list of all items in a project not necessarily committed to a sprint. | Backlog |
| **Backlog item** | A unit of work: `TASK`, `STORY`, `BUG` or `SUGGESTION`. | Item (or Task/Bug…) |
| **Item key** | Human reference `PROJECT-<sequence>`, e.g. `AUTH-142`. | Key |
| **Rank** | Lexicographic ordering value used for drag-and-drop ordering. | — |
| **Assignee** | The single user responsible for an item. | Assignee |
| **Sprint** | A time-boxed iteration with a committed set of items. | Sprint |
| **Sprint backlog** | Items committed to a specific sprint. | Sprint items |
| **Sprint snapshot** | Scope/points captured at sprint start, used for burndown and velocity. | — |
| **Team** | Group of users, optionally the lead of projects. | Team |
| **Project team** | A team associated with a project; defines visibility context. | Team |
| **Estimate** | Effort in story points for an item. | Estimate |
| **Velocity** | Completed points per sprint, historically. | Velocity |
| **Burndown** | Remaining work over the sprint against an ideal line. | Burndown |
| **Carry-over** | Unfinished sprint items moved to the backlog or the next sprint. | Carry over |
| **WIP limit** | Maximum items allowed in a board column. | Work-in-progress limit |
| **Cycle time** | Time from `IN_PROGRESS` to `DONE`. | Cycle time |

## 3. Time Tracking

| Term | Definition | UI label |
| :--- | :--- | :--- |
| **Work session** | A server-owned period of tracking, started and stopped by the user. | Session |
| **Time entry** | A recorded duration linked to an item; produced by a timer or entered manually. | Time entry |
| **Manual entry** | A time entry typed by the user rather than measured by the timer. | Manual time |
| **Idle segment** | A period with no input during a running timer, resolved by keep/discard/truncate. | Idle time |
| **Monotonic elapsed** | Duration measured by a non-decreasing clock, immune to system time changes. | — |
| **Timesheet** | Weekly aggregation of time entries by item. | Timesheet |
| **Sync batch** | A group of offline records sent to the server in one idempotent request. | — |
| **Offline queue** | Encrypted local list of records waiting to sync. | Pending sync |
| **Clock skew** | Difference between client elapsed and server-estimated elapsed. | — |

## 4. Monitoring & Privacy

| Term | Definition | UI label |
| :--- | :--- | :--- |
| **Monitoring session** | The monitoring counterpart of a work session; screenshots and heartbeats belong to it. | Session |
| **Screenshot** | An encrypted image captured at a random interval while a timer runs. | Screenshot |
| **Pending** | Uploaded screenshot inside the review window; owner-only. | In review |
| **Visible** | Screenshot whose review window has ended; managers with permission may view it. | Shared |
| **Privacy window** | The period (default 24 h, 1–72 h) during which the owner may delete a screenshot. | Review window |
| **Deletion** | Irreversible destruction of the blob, wrapped key and derived embeddings. | Delete permanently |
| **Tombstone** | Permanent metadata row proving a screenshot existed and was deleted. | Deleted by user |
| **Transparency log** | Personal record of everything captured about the user. | My activity log |
| **Heartbeat** | Periodic activity signal (active/idle seconds) with no content. | — |
| **Aggregation mode** | Tenant setting that hides per-person metrics when a cohort is below a threshold. | Privacy aggregation |
| **Crypto-shredding** | Deleting the encryption key so ciphertext is unrecoverable. | — |
| **Suspended** | Admin action that pauses capture and locks the agent UI. | Paused by admin |
| **Revoked** | Admin action that removes the device's tokens. | Signed out by admin |
| **Wipe** | Admin action that securely deletes local agent data. | Remote wipe |

## 5. Platform & Architecture

| Term | Definition |
| :--- | :--- |
| **Service** | Independently deployable backend component owning its data. |
| **API gateway** | Single ingress: routing, TLS, rate limits, ForwardAuth. |
| **ForwardAuth** | Traefik middleware delegating token verification to IAM. |
| **JWKS** | JSON Web Key Set published for token signature verification. |
| **Outbox** | Table written in the same transaction as a state change, then published as an event. |
| **Event** | Immutable fact in past tense (`item.created`) carrying tenant and actor. |
| **Projection** | Read-model table built from events for reporting. |
| **On-behalf-of (OBO)** | Acting with the caller's identity and permissions, used by AI and internal calls. |
| **Contract** | Versioned OpenAPI/AsyncAPI schema shared between services and clients. |
| **Expand/contract migration** | Schema change deployed in compatible steps so old and new code coexist. |
| **UUIDv7** | Time-ordered UUID; primary key format across the platform. |
| **Tenant scope** | The mandatory `tenant_id` filter applied to every tenant-owned query. |
| **RPO / RTO** | Recovery point objective / recovery time objective. |
| **SLO / SLI** | Service level objective / indicator. |
| **RED metrics** | Rate, Errors, Duration — the per-service baseline. |
| **ADR** | Architecture Decision Record, stored in `docs/DECISIONS.md`. |

## 6. Roles (system)

| Code | Meaning |
| :--- | :--- |
| `OWNER` | Tenant owner; full control including billing and closure. |
| `ADMIN` | Administers users, roles, settings and all projects. |
| `MANAGER` | Manages projects, sprints, team reports and team monitoring. |
| `LEAD` | Runs a team's board, membership and reports. |
| `MEMBER` | Does the work; owns their time and screenshots. |
| `VIEWER` | Read-only stakeholder. |
| `AI_AGENT` | Non-human service identity for the AI assistant. |

## 7. Status Values

| Entity | Values |
| :--- | :--- |
| Tenant | `TRIAL`, `ACTIVE`, `SUSPENDED`, `CLOSED` |
| User | `INVITED`, `ACTIVE`, `DISABLED` |
| Project | `ACTIVE`, `ARCHIVED` |
| Backlog item | `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `DONE`, `BLOCKED` |
| Priority | `LOW`, `MEDIUM`, `HIGH`, `URGENT` |
| Item type | `TASK`, `STORY`, `BUG`, `SUGGESTION` |
| Sprint | `PLANNED`, `ACTIVE`, `COMPLETED` |
| Work session | `RUNNING`, `PAUSED`, `ENDED`, `ORPHANED` |
| Screenshot | `PENDING`, `VISIBLE`, `DELETED`, `EXPIRED` |
| Export job | `QUEUED`, `RUNNING`, `DONE`, `FAILED` |

## 8. Naming Conventions Quick Reference

| Thing | Convention | Example |
| :--- | :--- | :--- |
| Permission | `domain:resource:action` | `task:item:create` |
| Role code | `UPPER_SNAKE` | `MANAGER` |
| DB table | `snake_case`, plural | `backlog_items` |
| DB column | `snake_case` | `assignee_id` |
| API field | `snake_case` | `estimate_points` |
| Event | `aggregate.past_tense` | `sprint.completed` |
| Error code | `lower_snake` | `assignee_not_eligible` |
| Service repo | `neatsprint-<name>` | `neatsprint-worklog` |
| Docker image | `ghcr.io/neatsprint/<name>` | `ghcr.io/neatsprint/task` |
| Env var | `UPPER_SNAKE` | `DATABASE_URL` |

---

## 9. Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-GLS-01 (Status value alignment — §7)**:
  - `Work session` in §7 lists `RUNNING, PAUSED, ENDED, ORPHANED`, whereas `neatsprint-worklog`
    persists `RUNNING, PAUSED, STOPPED` (`SESSION_STATES` in `db/models.py`). Reconcile §7 to
    `STOPPED`.
  - `Export job` in §7 lists `QUEUED, RUNNING, DONE, FAILED`, whereas `neatsprint-reports` uses
    `COMPLETED` in `ReportExport.status`. Reconcile §7 and `API_SPEC.md`.
- [ ] **IMP-GLS-02 (Docker image prefix — §8)**: Update the Docker image convention in §8 to
  `ghcr.io/neatsprint/neatsprint-<name>` to match `.github/workflows/release.yml`.

---

**End of Glossary**
