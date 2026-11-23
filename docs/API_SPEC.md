# NeatSprint — API Specification (Conventions & Catalogue)

> **Status**: Approved v1.0 · **Version**: 1.0 · **Last updated**: 2026-11-21
> **Owner**: Laksiri Fernando · **Author**: OpenCade (AI)
> **Supersedes**: `documents/step12-api-contracts.md`, `documents/step13-detailed-api-spec.md`
> **Machine-readable source of truth**: `neatsprint-contracts` repo (OpenAPI 3.1). This document
> explains the contract; the spec governs on conflict, and code generation follows the spec.

---

## 1. Global Conventions

| Item | Rule |
| :--- | :--- |
| Base URL (dev) | `http://localhost:8000/api/v1` (gateway) |
| Base URL (prod) | `https://api.neatsprint.com/api/v1` |
| Transport | HTTPS + HTTP/1.1 (HTTP/2 at the edge) |
| Content type | `application/json; charset=utf-8`; uploads use `multipart/form-data` or presigned PUT |
| Dates | ISO 8601 UTC (`2026-11-21T10:15:30Z`); dates without time as `YYYY-MM-DD` |
| Durations | Seconds, integer |
| IDs | UUIDv7 strings |
| Field naming | `snake_case` |
| Versioning | Path version `/api/v1`; additive changes only within a version |
| Deprecation | `Deprecation` + `Sunset` headers; minimum 90 days notice |
| Compression | gzip/br accepted |
| Tracing | `X-Request-ID` accepted or generated; echoed in response and logs |
| Timeout | Gateway 30 s upstream; clients should use 15 s + retry with backoff |

### 1.1 Required headers

| Header | When | Notes |
| :--- | :--- | :--- |
| `Authorization: Bearer <access_token>` | All protected endpoints | RS256 JWT |
| `X-Device-ID` | Desktop/mobile requests | Must match the token claim when present |
| `X-Request-ID` | Optional | UUID; generated if absent |
| `Idempotency-Key` | Required on specified write endpoints | UUIDv7; 24 h retention |
| `If-Match` / `ETag` | Optional optimistic concurrency | Supported on item update |

> `X-Tenant-ID` is **derived from the token**, not trusted from the client. Clients may send it
> for diagnostics; the server ignores it if it disagrees with `tid`.

### 1.2 Response envelope

Success:

```json
{
  "data": { "id": "018f...", "name": "Login flow" },
  "meta": { "request_id": "018f...", "trace_id": "..." }
}
```

List:

```json
{
  "data": [ { "id": "018f..." } ],
  "meta": {
    "page": 1, "per_page": 50, "total": 128,
    "next_cursor": "eyJpZCI6IjAxOGYifQ",
    "request_id": "018f..."
  }
}
```

Rules:

- Always wrap in `data`; never return a bare array at the top level.
- `meta` is present on every response (request id at minimum).
- `204 No Content` has no body.
- Nulls are explicit (`"assignee_id": null`), not omitted, for fields documented as nullable.

### 1.3 Errors (RFC 7807 + stable code)

```json
{
  "type": "https://docs.neatsprint.com/errors/permission-denied",
  "title": "Permission denied",
  "status": 403,
  "code": "permission_denied",
  "detail": "You do not have permission 'task:item:create' in this project.",
  "instance": "/api/v1/tasks/backlog",
  "request_id": "018f...",
  "errors": [ { "field": "title", "code": "too_long", "message": "Max 240 characters." } ]
}
```

| Status | When | Stable codes (examples) |
| :--- | :--- | :--- |
| 400 | Malformed request | `malformed_request` |
| 401 | Missing/invalid/expired token | `unauthenticated`, `token_expired`, `token_revoked` |
| 403 | Authenticated but not allowed | `permission_denied`, `tenant_mismatch`, `module_disabled`, `window_closed`, `not_yet_visible` |
| 404 | Not found **or not visible to this tenant** | `not_found` |
| 409 | State conflict | `duplicate_key`, `active_sprint_exists`, `timer_already_running`, `version_conflict`, `email_unavailable` |
| 410 | Gone permanently | `invitation_expired` |
| 413 | Payload too large | `payload_too_large` |
| 415 | Unsupported media | `unsupported_media_type` |
| 422 | Semantic validation | `invalid_transition`, `single_assignee`, `assignee_not_eligible` |
| 429 | Rate limited | `rate_limited`, `quota_exceeded` |
| 500 | Unexpected | `internal_error` |
| 503 | Dependency unavailable | `service_unavailable`, `dependency_unavailable` |

`code` is the contract; `title`/`detail` are for humans and may change.

### 1.4 Pagination

- Default `per_page=50`, max `200`.
- Offset pagination (`page`, `per_page`) for admin tables.
- Cursor pagination (`cursor`) for activity feeds, audit log, messages, screenshots.
- Sort parameter format `sort=-created_at,title` (`-` = descending) with allow-listed fields.

### 1.5 Idempotency

Required on:

- `POST /work/start`, `POST /work/stop`, `POST /work/sync`
- `POST /monitor/screenshots`
- `POST /tasks/backlog`, `PATCH /tasks/backlog/{id}`
- `POST /reports/exports`

Behaviour: same key + same body → replay stored response (status + body); same key + different
body → `409 idempotency_key_reused`.

### 1.6 Rate limits

| Bucket | Limit | Scope |
| :--- | :--- | :--- |
| `auth` | 20/min per IP + 10/min per email | login, reset |
| `public` | 60/min per IP | unauthenticated |
| `user` | 600/min per user | standard |
| `upload` | 20/min per device | screenshots |
| `export` | 5/hour per user | report exports |

Headers: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, `Retry-After`.

---

## 2. Endpoint Catalogue (MVP)

Legend: **P** = permission required. All endpoints require authentication unless noted.

### 2.1 IAM — `/api/v1/auth`

| Method | Path | Purpose | P |
| :--- | :--- | :--- | :--- |
| POST | `/auth/login` | Email/password login | public |
| POST | `/auth/refresh` | Rotate refresh token | public (refresh token) |
| POST | `/auth/logout` | Revoke current session | — |
| POST | `/auth/logout-all` | Revoke every session | — |
| POST | `/auth/forgot-password` | Start reset | public |
| POST | `/auth/reset-password` | Complete reset | public (token) |
| POST | `/auth/social/google` | Sign in with a Google ID token (GIS) | public |
| GET | `/auth/me` | Current user + permissions | — |
| GET | `/auth/sessions` | My sessions | — |
| DELETE | `/auth/sessions/{id}` | Revoke a session | — |
| GET | `/auth/verify` | ForwardAuth endpoint (internal) | internal |

### 2.2 IAM — `/api/v1/iam`

| Method | Path | Purpose | P |
| :--- | :--- | :--- | :--- |
| GET | `/iam/users` | List tenant users | `core:user:read` |
| POST | `/iam/users` | Create user directly | `core:user:invite` |
| GET | `/iam/users/{id}` | User detail | `core:user:read` or self |
| PATCH | `/iam/users/{id}` | Update profile/status | `core:user:update` or self (limited) |
| POST | `/iam/users/{id}/roles` | Assign roles | `core:role:manage` |
| DELETE | `/iam/users/{id}/roles/{roleId}` | Remove role | `core:role:manage` |
| POST | `/iam/users/{id}/avatar/presign` | Prepare an avatar upload | self or `core:user:update` |
| POST | `/iam/users/{id}/avatar/confirm` | Confirm the uploaded avatar | self or `core:user:update` |
| GET | `/iam/users/{id}/avatar` | Read the avatar | `core:user:read` or self |
| POST | `/iam/invitations` | Invite (collapses duplicate pending invite) | `core:user:invite` |
| GET | `/iam/invitations` | List invitations | `core:user:invite` |
| DELETE | `/iam/invitations/{id}` | Revoke | `core:user:invite` |
| POST | `/iam/invitations/{id}/resend` | Rotate the token and resend | `core:user:invite` |
| POST | `/iam/invitations/accept` | Accept invite | public (token) |
| GET | `/iam/roles` | List roles | `core:role:read` |
| POST | `/iam/roles` | Create custom role | `core:role:manage` |
| PATCH | `/iam/roles/{id}` | Update custom role | `core:role:manage` |
| DELETE | `/iam/roles/{id}` | Delete custom role | `core:role:manage` |
| GET | `/iam/permissions` | Permission catalogue | `core:role:read` |
| GET | `/iam/audit` | Audit log query | `report:audit:view` |
| GET | `/iam/notifications` | My notifications and unread count | signed-in user |
| POST | `/iam/notifications/{id}/read` | Mark one notification read | owner of the notification |
| POST | `/iam/notifications/read-all` | Mark all my notifications read | signed-in user |

> **Tenancy note (ADR-012)**: a tenant has many users, and each user logs in independently. Email
> addresses are globally unique, so an invitation for an email that already belongs to another
> tenant returns `409 email_unavailable` with neutral copy (never naming the other tenant). A
> tenant admin can invite, deactivate and re-role any number of users within their seat limit.

### 2.3 Core — `/api/v1/core`

| Method | Path | Purpose | P |
| :--- | :--- | :--- | :--- |
| GET | `/core/tenants/current` | Tenant detail | — |
| PATCH | `/core/tenants/current` | Update tenant | `core:tenant:update` |
| GET | `/core/tenants/current/settings` | Settings | — |
| PATCH | `/core/tenants/current/settings` | Update settings | `core:tenant:update` |
| GET | `/core/applications` | Module registry | — |
| GET | `/core/tenant-applications` | Enabled modules | — |
| PUT | `/core/tenant-applications/{code}` | Enable/disable | `core:tenant:update` |
| GET | `/core/plans` | Available plans | — |
| GET | `/core/usage` | Seats/projects usage | `core:tenant:read` |
| POST | `/core/tenants` | Provision tenant (operator) | `platform:tenant:create` |

### 2.4 Task — `/api/v1/tasks`

| Method | Path | Purpose | P |
| :--- | :--- | :--- | :--- |
| GET | `/tasks/projects` | List projects | `task:project:view` |
| POST | `/tasks/projects` | Create project | `task:project:create` |
| GET | `/tasks/projects/{id}` | Project detail | `task:project:view` |
| PATCH | `/tasks/projects/{id}` | Update | `task:project:edit` |
| POST | `/tasks/projects/{id}/archive` | Archive | `task:project:archive` |
| GET | `/tasks/projects/{id}/teams` | Project teams | `task:project:view` |
| PUT | `/tasks/projects/{id}/teams` | Set teams | `task:project:edit` |
| GET | `/tasks/projects/{id}/backlog` | Backlog list | `task:item:view` |
| GET | `/tasks/projects/{id}/board` | Board payload | `task:item:view` |
| POST | `/tasks/backlog` | Create item | `task:item:create` |
| GET | `/tasks/backlog/{id}` | Item detail | `task:item:view` |
| PATCH | `/tasks/backlog/{id}` | Update item | `task:item:edit` |
| POST | `/tasks/backlog/{id}/transition` | Status change | `task:item:transition` |
| POST | `/tasks/backlog/{id}/assign` | Assign/unassign | `task:item:assign` |
| POST | `/tasks/backlog/{id}/rank` | Reorder | `task:item:edit` |
| DELETE | `/tasks/backlog/{id}` | Soft delete | `task:item:delete` |
| GET | `/tasks/backlog/{id}/history` | Change history | `task:item:view` |
| GET | `/tasks/backlog/{id}/comments` | Comments | `task:item:view` |
| POST | `/tasks/backlog/{id}/comments` | Add comment | `task:item:comment` |
| PATCH | `/tasks/comments/{id}` | Edit comment | own or `task:item:moderate` |
| DELETE | `/tasks/comments/{id}` | Delete comment | own or `task:item:moderate` |
| POST | `/tasks/attachments` | Presign upload | `task:item:edit` |
| GET | `/tasks/attachments/{id}` | Download link | `task:item:view` |
| GET | `/tasks/sprints` | List sprints | `task:sprint:view` |
| POST | `/tasks/sprints` | Create sprint | `task:sprint:manage` |
| PATCH | `/tasks/sprints/{id}` | Update | `task:sprint:manage` |
| POST | `/tasks/sprints/{id}/start` | Start | `task:sprint:manage` |
| POST | `/tasks/sprints/{id}/complete` | Complete + carry-over | `task:sprint:manage` |
| POST | `/tasks/sprints/{id}/items` | Add items to sprint | `task:sprint:manage` |
| DELETE | `/tasks/sprints/{id}/items/{itemId}` | Remove item | `task:sprint:manage` |
| GET | `/tasks/sync?since=` | Delta for desktop | `task:item:view` |

**Project visibility.** A project with no linked teams is visible to every tenant member. When
teams are linked, only members of a linked team may list or open it; holders of
`task:project:create` (manager, admin, owner) always retain access. Denied requests return `404`
so project existence is not disclosed. Team membership is resolved through the Team internal API
and cached for 60 s per process; `team.member_added` / `team.member_removed` events invalidate the
affected entry immediately. Project-to-team mapping is read on every request, so mapping
changes take effect immediately.

**Assignees.** Creating, editing or assigning an item validates the assignee with IAM: the user
must exist, be `ACTIVE`, and — when the project has linked teams — belong to at least one of them.
Outsiders return `422 assignee_not_eligible`; an unreachable IAM returns
`503 dependency_unavailable`.

### 2.5 Team — `/api/v1/teams`

| Method | Path | Purpose | P |
| :--- | :--- | :--- | :--- |
| GET | `/teams` | List teams | `team:team:view` |
| POST | `/teams` | Create team | `team:team:manage` |
| GET | `/teams/{id}` | Detail | `team:team:view` |
| PATCH | `/teams/{id}` | Update | `team:team:manage` or team lead |
| POST | `/teams/{id}/members` | Add member | `team:member:manage` or lead |
| DELETE | `/teams/{id}/members/{userId}` | Remove member | `team:member:manage` or lead |
| GET | `/teams/{id}/members` | List members | `team:team:view` |

### 2.6 Worklog — `/api/v1/work`

| Method | Path | Purpose | P |
| :--- | :--- | :--- | :--- |
| POST | `/work/start` | Start timer | `work:timer:start` |
| POST | `/work/stop` | Stop timer | `work:timer:start` |
| GET | `/work/current` | Current session | — |
| POST | `/work/pause` | Pause (idle) | `work:timer:start` |
| POST | `/work/resume` | Resume | `work:timer:start` |
| POST | `/work/idle` | Report idle segment | `work:timer:start` |
| POST | `/work/sync` | Batch offline entries | `work:log:write` |
| GET | `/work/entries` | List entries | `work:log:view_own` / `view_team` |
| POST | `/work/entries` | Manual entry | `work:log:write` |
| PATCH | `/work/entries/{id}` | Edit entry | owner + `work:log:write` |
| DELETE | `/work/entries/{id}` | Delete entry | owner within 24 h |
| GET | `/work/timesheet` | Weekly aggregate | `work:log:view_own` / `view_team` |
| GET | `/work/export` | CSV export | `report:export` |

### 2.7 Monitoring — `/api/v1/monitor`

| Method | Path | Purpose | P |
| :--- | :--- | :--- | :--- |
| POST | `/monitor/devices` | Register device | — |
| GET | `/monitor/devices` | My devices | — |
| DELETE | `/monitor/devices/{id}` | Revoke device | `monitor:device:manage` or self |
| POST | `/monitor/devices/{id}/wipe` | Remote wipe | `monitor:device:manage` |
| POST | `/monitor/sessions/start` | Start monitoring session | `work:timer:start` |
| POST | `/monitor/sessions/{id}/heartbeat` | Activity pulse | `work:timer:start` |
| POST | `/monitor/sessions/{id}/stop` | Stop session | `work:timer:start` |
| POST | `/monitor/screenshots` | Upload (pending) | `work:timer:start` |
| POST | `/monitor/screenshots/presign` | Presigned PUT | `work:timer:start` |
| GET | `/monitor/screenshots/mine` | My gallery | — |
| DELETE | `/monitor/screenshots/{id}` | Privacy delete | owner, inside window |
| GET | `/monitor/screenshots` | Manager gallery | `monitor:data:view_team` / `view_all` |
| GET | `/monitor/screenshots/{id}/content` | Decrypt + stream | owner or `monitor:data:view_*` |
| GET | `/monitor/sessions` | Session list | `monitor:data:view_team` |
| GET | `/monitor/transparency` | Personal log | self |
| GET | `/monitor/policy` | Effective capture policy | — |

**Deletion contract** (important):

```http
DELETE /api/v1/monitor/screenshots/{id}
→ 204 No Content            # blob + embeddings destroyed, tombstone written
→ 403 window_closed         # after privacy window
→ 404 not_found             # foreign tenant or unknown
→ 409 deletion_in_progress  # retry shortly
```

### 2.8 Reports — `/api/v1/reports`

| Method | Path | Purpose | P |
| :--- | :--- | :--- | :--- |
| GET | `/reports/time` | Time by project/user/team | `report:productivity:view` |
| GET | `/reports/completion` | Created vs completed | `report:productivity:view` |
| GET | `/reports/velocity` | Velocity, last N sprints | `report:agile:view` |
| GET | `/reports/burndown` | Sprint burndown | `report:agile:view` |
| GET | `/reports/monitoring` | Activity + deletion summary | `report:monitoring:view` |
| GET | `/reports/transparency` | Personal transparency | self |
| POST | `/reports/exports` | Queue export | `report:export` |
| GET | `/reports/exports/{id}` | Export status | `report:export` |
| GET | `/reports/exports` | My export jobs | `report:export` |

### 2.9 Chat (P2) — `/api/v1/chat`

| Method | Path | Purpose |
| :--- | :--- | :--- |
| GET | `/chat/channels` | My channels |
| GET | `/chat/channels/{id}/messages` | History (cursor) |
| POST | `/chat/channels/{id}/messages` | Send |
| PATCH | `/chat/messages/{id}` | Edit own |
| DELETE | `/chat/messages/{id}` | Soft delete own/mod |
| POST | `/chat/channels/{id}/read` | Mark read |
| GET | `/chat/ws` | WebSocket upgrade (ticket-authenticated) |

### 2.10 AI (P3) — `/api/v1/ai`

| Method | Path | Purpose |
| :--- | :--- | :--- |
| POST | `/ai/ask` | Ask a question (SSE stream) |
| POST | `/ai/summaries/work` | Work summary for a period |
| POST | `/ai/summaries/standup` | Standup draft |
| POST | `/ai/drafts/backlog-item` | Draft item (no write) |
| POST | `/ai/actions/{id}/confirm` | Confirm a drafted action |
| GET | `/ai/conversations` | My conversations |
| GET | `/ai/audit` | AI audit (admin) |

### 2.11 Platform endpoints

| Method | Path | Purpose |
| :--- | :--- | :--- |
| GET | `/healthz` | Liveness (no auth, no DB) |
| GET | `/readyz` | Readiness (DB/Redis check) |
| GET | `/metrics` | Prometheus (internal only) |
| GET | `/openapi.json` | Spec (dev/staging; restricted in prod) |

---

## 3. Representative Payloads

### 3.1 Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "jane@acme.test",
  "password": "correct horse battery staple",
  "device": { "name": "Jane's laptop", "platform": "windows", "app_version": "1.4.0" }
}
```

```json
{
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 900,
    "refresh_token": "rt_018f...",
    "user": {
      "id": "018f1c...",
      "email": "jane@acme.test",
      "full_name": "Jane Doe",
      "tenant_id": "018f0a...",
      "roles": ["MANAGER"],
      "permissions": ["task:project:view", "task:item:create", "..."]
    }
  },
  "meta": { "request_id": "018f2b..." }
}
```

### 3.2 Create backlog item

```http
POST /api/v1/tasks/backlog
Idempotency-Key: 018f3c9e-...
Content-Type: application/json

{
  "project_id": "018f1d...",
  "type": "TASK",
  "title": "Implement device-bound sessions",
  "description": "Bind refresh tokens to the device key pair.",
  "priority": "HIGH",
  "estimate_points": 5,
  "assignee_id": "018f1c..."
}
```

```json
{
  "data": {
    "id": "018f3d...",
    "key": "AUTH-142",
    "status": "TODO",
    "assignee_id": "018f1c...",
    "created_at": "2026-11-21T10:15:30Z",
    "version": 1
  },
  "meta": { "request_id": "..." }
}
```

### 3.3 Offline sync batch

```http
POST /api/v1/work/sync
Idempotency-Key: 018f4a...
```

```json
{
  "device_id": "018f0b...",
  "batch_id": "018f4a...",
  "entries": [
    {
      "client_id": "018f4b...",
      "item_id": "018f3d...",
      "started_at": "2026-11-21T08:00:00Z",
      "duration_seconds": 1830,
      "monotonic_elapsed_seconds": 1830,
      "source": "TIMER",
      "comment": "Offline work"
    }
  ],
  "deleted_screenshot_client_ids": ["018f4c..."]
}
```

```json
{
  "data": {
    "accepted": 1,
    "duplicates": 0,
    "rejected": [],
    "server_time": "2026-11-21T11:05:00Z"
  }
}
```

### 3.4 Screenshot upload (multipart)

```http
POST /api/v1/monitor/screenshots
Content-Type: multipart/form-data; boundary=...

file=<binary>
metadata={"session_id":"018f5a...","captured_at":"2026-11-21T10:00:00Z",
          "display_index":0,"width":2560,"height":1440,"content_hash":"sha256:..."}
```

```json
{
  "data": {
    "id": "018f5b...",
    "state": "PENDING",
    "visible_after": "2026-11-22T10:00:00Z",
    "deletable_until": "2026-11-22T10:00:00Z"
  }
}
```

### 3.5 Report query

```http
GET /api/v1/reports/time?from=2026-11-01&to=2026-11-21&group_by=project&team_id=...
```

```json
{
  "data": {
    "totals": { "seconds": 184320, "entries": 412 },
    "series": [
      { "key": "AUTH", "label": "Authentication", "seconds": 64800 },
      { "key": "BILL", "label": "Billing", "seconds": 40320 }
    ],
    "scope": "team"
  },
  "meta": { "generated_at": "2026-11-21T11:10:00Z", "cached": true }
}
```

---

## 4. Internal Service APIs

Service-to-service calls are authenticated with a service token (`aud=service:<name>`) and are
**never** routed through the public gateway.

| Caller | Callee | Endpoint | Purpose |
| :--- | :--- | :--- | :--- |
| Task | IAM | `POST /internal/users/lookup` | Validate assignees (batch, tenant-scoped) |
| Team | IAM | `POST /internal/users/lookup` | Membership validation |
| Task / Worklog | Team | `GET /internal/teams/{id}/members` | Access scope |
| Worklog | Task | `GET /internal/items/{id}` | Item/project existence |
| Monitoring | Worklog | `GET /internal/sessions/{id}` | Session validity |
| Reports | all | event stream only | Projections |
| AI | all | public APIs with user token | On-behalf-of |

Internal endpoints live under `/internal/*`, require service auth, are not exposed by Traefik, and
are versioned with the service.

---

## 5. Webhooks (Phase 2)

| Event | Payload | Signature |
| :--- | :--- | :--- |
| `item.created`, `item.transitioned` | item + project summary | `X-NeatSprint-Signature: sha256=...` |
| `sprint.started`, `sprint.completed` | sprint snapshot | same |
| `time.entry_recorded` | anonymised entry | same |
| `screenshot.deleted` | tombstone metadata only | same |

Retries: 5 attempts with exponential backoff; delivery log exposed in the admin UI (P2).

---

## 6. API Governance

1. The OpenAPI document is generated from code and validated in CI (`spectral`, `schemathesis`).
2. A breaking change requires: major version path or a new field with a deprecation window, an
   ADR, and a changelog entry.
3. Every response schema has examples; every endpoint has at least one contract test.
4. TypeScript clients are generated in CI; hand-written request types are rejected in review.
5. Error `code` values are a closed list per service; new codes require a test and docs update.

---

**End of API Specification**
