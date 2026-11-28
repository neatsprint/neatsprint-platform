# NeatSprint — Security & Privacy Model

> **Status**: Approved v1.0 · **Version**: 1.0 · **Last updated**: 2026-11-21
> **Owner**: Laksiri Fernando (approval) · **Author**: OpenCade (AI)
> **Supersedes**: `documents/step8-security-and-privacy-model.md`, `step9`, `step10`, `step11`, `step16`
> **Related**: `ARCHITECTURE.md` §4/§6, `DATA_MODEL.md`, `TEST_PLAN.md`, `DECISIONS.md`

---

## 1. Security Objectives

| Objective | Why it matters | Primary controls |
| :--- | :--- | :--- |
| **Tenant isolation** | One leak destroys the product's credibility | Token-derived tenant, repository scoping, isolation tests |
| **Least privilege** | Employees must not see more than their role allows | Feature permissions, resource-scope checks, deny-by-default |
| **Privacy honesty** | Monitoring is only acceptable if it is transparent and revocable | Privacy window, tombstone audit, personal transparency log |
| **Session integrity** | Stolen tokens must not become stolen accounts | Short-lived JWTs, rotating refresh, device binding, revocation |
| **Data-at-rest safety** | Laptops get lost; storage gets misconfigured | SQLCipher locally, encrypted volumes, KMS envelope for blobs |
| **Auditability** | Compliance and incident response need evidence | Append-only audit log, view audits, AI audit |
| **Supply-chain integrity** | Build pipelines are a prime target | Signed images, SBOM, pinned deps, secret scanning |

**Non-negotiable**: a `403`/`404` must never be turned into data exposure; a "deleted" screenshot
must never be recoverable by any role, including platform operators.

---

## 2. Threat Model (STRIDE)

Scope: public API, gateway, services, web app, desktop agent, storage, CI/CD.
Method: data-flow review per component; threats ranked by impact × likelihood.

| # | Category | Threat | Impact | Mitigation | Verified by |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T-01 | Spoofing | Stolen access token replayed from another machine | Account takeover | Short TTL, device-bound refresh, `X-Device-ID` match, revocation | TC-IAM-012, TC-DSK-017 |
| T-02 | Spoofing | Forged `X-User-ID`/`X-Tenant-ID` headers | Tenant impersonation | Gateway strips inbound headers; services validate JWT via JWKS | TC-IAM-014, TC-SEC-005 |
| T-03 | Tampering | Client alters time entries / durations | Billing fraud | Monotonic client clock, server clamp, anomaly flags, audit | TC-WRK-004, TC-WRK-008 |
| T-04 | Tampering | Modified desktop binary disables monitoring | False records | Code signing, update signature, heartbeat, process watchdog | TC-DSK-013 |
| T-05 | Repudiation | User denies deleting/viewing a screenshot | Dispute | Append-only audit, deletion audit, view audit | TC-MON-007, TC-MON-015 |
| T-06 | Information disclosure | Cross-tenant IDOR on any resource | Catastrophic leak | Tenant filter helper, 404 for foreign ids, isolation suite | TC-SEC-004..009 |
| T-07 | Information disclosure | Deleted screenshot still retrievable from storage/backup | Privacy breach | Blob delete + tombstone, blobs excluded from backups, embeddings purged | TC-MON-003..005 |
| T-08 | Information disclosure | Manager sees pending (in-window) screenshots | Privacy violation | Pending state, `not_yet_visible` for non-owners | TC-MON-006 |
| T-09 | Information disclosure | Secrets in git, logs, or images | Full compromise | Secret scan, no secrets in env files committed, log scrubbing | CI gates |
| T-10 | Denial of service | Upload flood / auth brute force | Outage | Rate limits per IP/user/device, quotas, body size caps | TC-PERF, TC-IAM-002 |
| T-11 | Elevation of privilege | Member grants themselves a role | Full tenant takeover | Privilege guard, permission required to grant, audit | TC-SEC-003 |
| T-12 | Elevation of privilege | Report query with foreign `team_id` leaks data | Leak | Scoped query builder, 404/empty result | TC-SEC-008 |
| T-13 | Elevation of privilege | AI answers beyond caller permissions | Leak via assistant | On-behalf-of token, intersection of permissions, audit | TS-10 |
| T-14 | Supply chain | Typosquatted dependency / compromised base image | Backdoor | Lockfiles, pinned digests, Trivy, Dependabot, review | CI gates |
| T-15 | Insider | Platform operator reads tenant screenshots | Trust breach | Role separation, break-glass audit, encryption access logged | Audit review |
| T-16 | Physical | Stolen laptop with local DB | Data exposure | SQLCipher, OS-keychain-wrapped key, remote wipe | TC-DSK-007, TC-DSK-012 |
| T-17 | Privacy | Hidden capture (no indicator) | Legal/ethical breach | Mandatory visible indicator + toast; no silent mode in code | Manual checklist |
| T-18 | Availability | Redis loss blocks all auth | Outage | Fail-closed but documented; DB fallback for permissions | TC-REL-002 |

Residual risks accepted for MVP:

- A determined user with admin rights on their own machine can tamper with the agent; heartbeat
  and audit detect it, prevention is out of scope.
- Single-region deployment has a regional outage risk.
- No third-party penetration test before v1.0 (scheduled post-MVP).

### 2.1 M5 hardening review (2026-11-24)

| Area | Finding | Status |
| :--- | :--- | :--- |
| Cross-tenant IDOR | Automated probe created a second tenant and attempted project, item, team, user and time reads | **PASS** — every foreign read returned `404` or an empty scoped result (`scripts/security/cross_tenant_probe.py`) |
| Tenant isolation | Task/Team use PostgreSQL RLS; other services filter `tenant_id` explicitly | Verified in code and probe |
| Auth headers | Gateway strips inbound `X-User-ID`/`X-Tenant-ID`; services verify JWTs via JWKS | Verified |
| Cookies | Access/refresh cookies are `HttpOnly`, `SameSite=Lax`, `Secure` in production, `Cache-Control: no-store` | Verified |
| Rate limits | Gateway applies per-IP auth/public buckets and per-user buckets | Verified in Traefik config |
| Security headers | Gateway and Next.js set nosniff, frame-deny, referrer and CSP headers | Added in M5 |
| Uploads | MIME allow-list, magic-byte sniffing, 25 MB cap, dedupe hash, quota; ClamAV INSTREAM scanner fails closed | **PASS** — EICAR `422 malware_detected`; scanner down `503 dependency_unavailable` |
| Screenshot deletion | Blob delete + tombstone + audit + view log | Verified live |
| Desktop agent | Device binding verified: Ed25519 key pair in the OS keychain, per-request proof over method/path/timestamp/nonce/body hash, nonce replay rejected; SQLCipher and update signing still open | **Partial (M3-T23)** |
| Dependency/container scans | Dependabot, CodeQL and Trivy 0.69.3 on every image | **PASS** — 0 high/critical across 10 images (`docs/SBOM.md`) |
| Login lockout | Redis counter, 5 failures / 15 minutes, shared across IAM replicas | **PASS** — `429 account_locked` verified |
| Secrets | No secrets in git; `.env` ignored; rotation runbook added | Verified |

Open M5 security work: desktop-agent verification (ADR-019) and the staging/UAT gates.

---

## 3. Authentication

### 3.1 Password authentication

- **Argon2id** with parameters `m=64MB, t=3, p=4` (tuned to ~250 ms on target hardware).
- Minimum 10 characters; breached-password check (k-anonymity API or bundled list) at registration
  and reset.
- Login responses are uniform ("Invalid email or password") with constant-time comparison.
- Progressive lockout: 5 failures → 15 min per account+IP pair, audited; no account enumeration.
- Password change invalidates all other sessions.
- **Global email uniqueness (ADR-012)**: an email identifies exactly one account in one tenant, so
  login needs no workspace selector. Inviting an email that already exists elsewhere returns a
  neutral `409 email_unavailable`; the API never discloses which tenant holds it.

### 3.2 Tokens

| Token | Format | Lifetime | Storage | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Access | RS256 JWT | 15 min | Web: httpOnly cookie via BFF; Desktop: OS keychain; Mobile: SecureStore | Never `localStorage` |
| Refresh | Opaque or JWT, hashed at rest | 7 days | Same as access | Rotated every use; family revoked on reuse |
| Device | Key pair + registered public key | 30 days rolling | Private key in OS keychain/TPM | Requests signed over nonce + method + path + body hash |
| Service | JWT `aud=service:<name>` | 5 min | In-memory | Internal calls only |

**Claims**: `iss`, `aud`, `sub`, `tid`, `sid`, `jti`, `roles`, `scope`, `device_id?`, `iat`, `exp`.
**Signing keys**: two active kids during rotation; JWKS published with cache headers; private keys
in KMS/Vault, never on disk.

### 3.3 Social login

- OAuth2 + OIDC with PKCE and `state`/`nonce` validation.
- `email_verified` must be true.
- Linking rules: an existing user with the same verified email may link; otherwise require an
  invitation unless the tenant enables `domain_auto_join`.
- Never auto-join across tenants on a shared email domain without explicit tenant opt-in.

### 3.4 Device binding (desktop/mobile)

Replaces the reference design's CPU-serial/MAC fingerprinting (spoofable and privacy-invasive).

```text
1. Agent generates Ed25519 key pair on first run.
2. Public key registered with IAM; private key stays in OS keychain (TPM-backed where available).
3. Login returns tokens bound to device_id = hash(public_key).
4. Each API call includes X-Device-ID and DPoP-style proof:
     proof = sign(private_key, method + path + sha256(body) + nonce + timestamp)
5. Server verifies signature, timestamp (±60 s), nonce uniqueness, and device status.
6. Revoking a device invalidates refresh tokens and rejects further proofs.
```

Fallback for browsers: no device binding; rely on httpOnly cookies, CSRF protection and refresh
rotation.

---

## 4. Authorisation

### 4.1 Model

```text
Access = f( permission in token, tenant match, resource scope, module enabled )
```

- **Deny by default.** Every route declares its permission; a missing declaration fails the
  route-registration test.
- **Two gates**: gateway (signature, expiry, coarse check) and service (JWKS, permission, scope).
- **Resource scope** is resolved in the owning service:
  - Task: a project with no linked teams is open to the tenant; otherwise membership in a
    linked team is required (`task:project:create` holders bypass).
  - Team: membership or tenant-wide permission.
  - Worklog/Monitoring: own / team / tenant scope.
- **Assignment scope.** An assignee must be an active tenant user and, for team-scoped projects,
  a member of a linked team; IAM is the source of truth, cached 60 s.
- Permission checks are centralised in a dependency/decorator, never copy-pasted.

### 4.2 Roles

| Code | Name | Summary |
| :--- | :--- | :--- |
| `OWNER` | Tenant Owner | Full control incl. billing, tenant closure, all monitoring |
| `ADMIN` | Administrator | Users, roles, settings, all projects, all monitoring |
| `MANAGER` | Project Manager | Projects, sprints, team reports, team monitoring |
| `LEAD` | Team Lead | Team board, team membership, team reports |
| `MEMBER` | Team Member | Own work, own time, own screenshots, comments |
| `VIEWER` | Stakeholder | Read-only across projects they can see |

Roles are **additive**; a user may hold several. `AI_AGENT` is a non-human service identity.

### 4.3 Permission catalogue (MVP)

Format: `domain:resource:action`.

**Core / IAM**

| Permission | OWNER | ADMIN | MANAGER | LEAD | MEMBER | VIEWER |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| `core:tenant:read` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `core:tenant:update` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `core:role:read` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `core:role:manage` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `core:user:read` | ✅ | ✅ | ✅ | ✅ | ✅* | ✅ |
| `core:user:invite` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `core:user:update` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

\* `MEMBER` may read users only within their teams/projects (directory scope).

**Task**

| Permission | OWNER | ADMIN | MANAGER | LEAD | MEMBER | VIEWER |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| `task:project:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `task:project:create` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `task:project:edit` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `task:project:archive` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `task:item:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `task:item:create` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `task:item:edit` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `task:item:transition` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `task:item:assign` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `task:item:delete` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `task:item:comment` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `task:item:moderate` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `task:sprint:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `task:sprint:manage` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |

**Team**

| Permission | OWNER | ADMIN | MANAGER | LEAD | MEMBER | VIEWER |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| `team:team:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `team:team:manage` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `team:member:manage` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |

**Worklog**

| Permission | OWNER | ADMIN | MANAGER | LEAD | MEMBER | VIEWER |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| `work:timer:start` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `work:log:write` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `work:log:view_own` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `work:log:view_team` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `work:log:view_all` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `work:log:edit_any` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

**Monitoring**

| Permission | OWNER | ADMIN | MANAGER | LEAD | MEMBER | VIEWER |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| `monitor:data:view_own` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `monitor:data:view_team` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `monitor:data:view_all` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `monitor:config:manage` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `monitor:device:manage` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

Note: viewing **content** is additionally constrained by the pending/visible state and the
deletion tombstone. No permission grants access to deleted pixels.

**Reports**

| Permission | OWNER | ADMIN | MANAGER | LEAD | MEMBER | VIEWER |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| `report:productivity:view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `report:agile:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `report:monitoring:view` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `report:audit:view` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `report:export` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `report:transparency:view` (self) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**AI (P3)**

| Permission | OWNER | ADMIN | MANAGER | LEAD | MEMBER | VIEWER |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| `ai:use` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `ai:audit:view` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

### 4.4 Escalation guards

1. You cannot grant a role containing a permission you do not hold.
2. You cannot remove the last `OWNER`.
3. You cannot change your own roles.
4. All role changes require an audit entry in the same transaction.
5. Permission cache is invalidated on change; a stale cache may never grant a **new** permission
   (invalidation is publish-first, then apply).

---

## 5. Tenant Isolation

| Layer | Control |
| :--- | :--- |
| Token | `tid` is authoritative; mismatched `X-Tenant-ID` → `403 tenant_mismatch` |
| Repository | Base repository requires a tenant context; unscoped query raises |
| Query | `WHERE tenant_id = :tid` on every tenant-owned read/write, including counts and aggregates |
| IDs | UUIDv7 (unguessable); foreign IDs return `404`, never `403`, to avoid existence leaks |
| Storage | Object keys prefixed `tenant/<tenant_id>/...`; presigned URLs scoped and short-lived |
| Cache | Keys include `tenant_id`; no global key may contain tenant data |
| Logs | `tenant_id` included, PII excluded |
| Reports | Every projection row carries `tenant_id`; aggregation cannot cross tenants |
| Admin | No platform-wide data browser in MVP; operator actions are audited and break-glass |
| Invitations | An email held by another tenant receives a neutral conflict; no tenant name, no ownership leak |

A dedicated isolation test suite runs on every PR (`TEST_PLAN.md` §6.2). A new endpoint without an
isolation test fails CI.

---

## 6. Privacy Model (the flagship feature)

### 6.1 Principles

1. **Transparency** — recording is always visible: tray indicator, toast, personal log.
2. **Containment** — capture only during an active timer, only on selected displays, never audio,
   keyboard content, clipboard or camera.
3. **Agency** — the user can inspect and delete their own pending screenshots.
4. **Irreversibility** — deletion destroys pixel data and derived text permanently.
5. **Accountability** — deletion is not anonymous; it is logged and visible as a tombstone.

### 6.2 Privacy window (canonical)

```text
tenant setting privacy_window_hours (default 24, range 1–72)

capture ──► encrypted upload ──► PENDING (owner-only)
                                   │
                    ┌──────────────┼───────────────┐
                    │              │               │
              owner deletes   window ends     owner approves
                    │              │               │
                 DELETED        VISIBLE         VISIBLE
             (blob+embeddings      │
                destroyed)         │
                              manager view (audited)
                                   │
                              retention expiry
                                   │
                                EXPIRED (tombstone)
```

Rules:

- Managers cannot see pending content, even with `monitor:data:view_all`.
- Deletion inside the window is immediate and idempotent.
- After the window, deletion is refused with `403 window_closed`; retention handles the rest.
- Tombstones remain: `id`, `user_id`, `captured_at`, `deleted_at`, `deleted_by`, `source`.
  No path, no hash of content, no thumbnail, no caption.
- An exception exists for **legal hold** (Phase 3): retention is suspended, but user deletion inside
  the window still applies unless the hold explicitly covers that user's captures and the user is
  notified in-product.

### 6.3 What is never captured

- Audio, video, camera, clipboard, keystroke contents, browser history, files, private messages.
- Screens outside the tenant's configured displays.
- Anything while the timer is stopped or the device is suspended.

### 6.4 Transparency log

Each user has an immutable personal log: timestamp, project/item, capture status (stored/deleted),
session duration, device. It is readable by the user and by nobody else (except aggregated counts
for compliance). It is the product's ethical backstop.

---

## 7. Encryption & Key Management

| Data | At rest | In transit | Keys |
| :--- | :--- | :--- | :--- |
| Postgres | Volume encryption (cloud) + TDE where available | TLS | Cloud KMS |
| Screenshots | **KMS envelope**: data key per object, wrapped by tenant key; AES-256-GCM | TLS 1.3 | Tenant key in KMS; data keys never persisted unwrapped |
| Local desktop DB | SQLCipher (AES-256) | — | Argon2id(user password + device salt), wrapped in OS keychain |
| Backups | Encrypted by provider, separate key | TLS | KMS |
| Secrets | Vault / cloud secret manager, CSI mount | TLS | Rotation schedule |
| Password hashes | Argon2id | — | — |

**Why envelope, not end-to-end**: managers must view screenshots and the AI (P3) must summarise
them. True E2E would make both impossible. Instead: encryption at rest with strict access control,
short-lived decryption only for authorised requests, and per-access audit. This is recorded as
ADR-005 and must be disclosed honestly in marketing and the privacy policy.

**Deletion and crypto-shredding**: deleting a screenshot destroys the blob and the wrapped data key.
Even if a storage snapshot survived, the key is gone.

**Key rotation**: tenant data keys rotate annually (re-wrap, no re-encrypt needed for envelope);
JWT signing keys rotate every 90 days with overlapping JWKS; secrets every 180 days.

---

## 8. AI Guardrails (Phase 3)

| Guardrail | Implementation |
| :--- | :--- |
| **Permission mirror** | AI calls services with the caller's token (OBO); effective permission = AI service permission ∩ caller permission |
| **Deleted data** | Structured filter excludes `state IN (DELETED, EXPIRED)`; embeddings cascade-deleted in the same job |
| **No training** | Provider configured for zero-retention/no-training; contractual DPA clause |
| **PII scrubbing** | Emails, phone numbers, tokens replaced before provider call; raw text never leaves the region |
| **Write confirmation** | AI may only create drafts; a user action is required to persist |
| **Audit** | Prompt, tool calls, source IDs, response, tokens, latency, model version |
| **Kill switch** | Per-tenant and global feature flag disables AI instantly |
| **Prompt injection** | Retrieved content is treated as data; tool calls restricted to allow-listed operations with schema validation |
| **Cost control** | Per-tenant token quotas and alerts |

---

## 9. Desktop Agent Security

| Control | Implementation |
| :--- | :--- |
| Code signing | Authenticode (Windows), Developer ID + notarisation (macOS), Ed25519 updates |
| Update integrity | Signature verified before install; monotonic version prevents downgrade |
| Local encryption | SQLCipher; key wrapped in OS keychain; never written to disk unwrapped |
| Tamper detection | Watchdog process, heartbeat, startup integrity check of critical resources |
| Secure time | Monotonic clock for durations; server clamp on sync |
| Remote controls | Suspend, revoke, wipe — delivered as signed commands, acknowledged |
| Least privilege | No admin rights required to run; no kernel drivers in MVP |
| Diagnostics | Local log readable by the user; no screen content in logs |
| Uninstall | Removes local DB and temp captures; documented residual files |
| Crash reports | Opt-in, PII-scrubbed, no screenshots attached |

---

## 10. Application Security Controls (Web)

- CSP with nonces, `default-src 'self'`, no inline scripts, strict `connect-src`.
- `Strict-Transport-Security`, `X-Content-Type-Options`, `Referrer-Policy: no-referrer`,
  `Permissions-Policy` disabling camera/microphone/geolocation.
- Cookies: `HttpOnly`, `Secure`, `SameSite=Lax`, `__Host-` prefix.
- CSRF: double-submit token for cookie-authenticated mutations + Origin check.
- Output encoding by framework; no `dangerouslySetInnerHTML` without sanitisation (DOMPurify).
- File uploads: allow-list of types, size caps, content sniffing, re-encode images.
- SSRF: no user-supplied URLs fetched server-side in MVP.
- Dependency policy: no unmaintained packages; `npm audit`/`pip-audit` clean at release.

---

## 11. Audit & Monitoring

| Event | Logged fields | Retention |
| :--- | :--- | :--- |
| Login success/failure, lockout | actor, ip, ua, result, request_id | 1 year |
| Token refresh/reuse detection | session, device, result | 1 year |
| Role/permission change | before/after, actor | 7 years (archive) |
| Invitation lifecycle | actor, email hash, result | 1 year |
| Screenshot view | viewer, subject, screenshot id, ip | 1 year |
| Screenshot deletion | actor, screenshot id, source, blob/embedding confirmation | 7 years |
| Device register/revoke/wipe | actor, device, reason | 1 year |
| Report export | actor, filters hash, row count | 1 year |
| AI prompt/tool/response | actor, model, source ids | 1 year |
| Admin break-glass access | actor, justification, scope | 7 years |

Alerts (see `DEVOPS.md`): repeated 401/403 spikes, cross-tenant attempts, deletion rate anomaly,
audit write failures, KMS access errors.

---

## 12. Data Lifecycle & Retention

| Data | Retention | Deletion mechanism |
| :--- | :--- | :--- |
| Screenshot blobs | tenant setting (default 30 d) | lifecycle job + object delete |
| Screenshot tombstones | 1 year | partition drop |
| Time entries | 7 years | archive + purge |
| Audit log | 1 year hot / 7 years archive | partition drop |
| Soft-deleted items | 30 days | nightly purge |
| Sessions | 30 days after expiry | purge |
| Invitations | 30 days after expiry | purge |
| AI conversations | 90 days | purge |
| Backups | 30 days | provider lifecycle |

**GDPR/CCPA operations**

| Right | Implementation |
| :--- | :--- |
| Access | Self-service JSON export of profile, sessions, entries, captures metadata |
| Rectification | Profile and entry edit endpoints |
| Erasure | Anonymise identity (`Deleted User`, void email), delete credentials/social, delete screenshots + embeddings, retain anonymised work history for tenant reporting |
| Restriction | Account suspension stops processing except retention |
| Portability | JSON/CSV export via reports |
| Objection | Monitoring can be paused by the tenant admin for a user; record kept |

Erasure is asynchronous with a status endpoint; completion is audited and reported to the tenant
admin.

---

## 13. Incident Response

| Phase | Action |
| :--- | :--- |
| Detect | Alerts, user report, audit anomaly, dependency advisory |
| Triage | Severity matrix; S1 = data exposure, privacy breach, auth bypass, destructive data loss |
| Contain | Revoke tokens/devices, rotate keys, disable module flag, block IP |
| Eradicate | Patch, deploy hotfix, verify with targeted tests |
| Recover | Restore from backup if needed, monitor 72 h |
| Notify | Tenant admins within 24 h for confirmed personal-data incidents; regulator per GDPR (72 h) |
| Learn | Post-incident review within 5 days; add regression test; update threat model |

**Break-glass**: a platform operator can access tenant metadata only via an audited, time-boxed,
justified elevation. Screenshot content is never accessible to operators.

---

## 14. Secure SDLC

| Stage | Control |
| :--- | :--- |
| Design | Threat model updated per epic; ADR for security-relevant choices |
| Code | Reviewed PRs, mandatory authz checklist, no secrets, parameterised SQL |
| Test | Authz matrix, isolation suite, privacy deletion tests, upload abuse tests |
| Build | Pinned deps, lockfiles, SBOM, signed images (cosign), Trivy scan |
| Release | Signed artefacts, changelog, rollback plan, feature flags |
| Operate | Least-privilege IAM, no SSH to prod, audited admin, encrypted backups |
| Maintain | Weekly dependency PRs, monthly patch window, quarterly access review |

---

## 15. Compliance Mapping (MVP)

| Framework (in-scope subset) | How we address it |
| :--- | :--- |
| **GDPR** | Lawful basis via tenant contract; DPA; DSAR endpoints; retention; erasure; sub-processor list |
| **OWASP ASVS L2** | Auth, session, access control, validation, crypto, logging items tracked in M5 checklist |
| **OWASP Top 10** | Covered by controls in §3–§10; verified by tests and ZAP baseline |
| **SOC 2 readiness (future)** | Audit logs, access reviews, change management, incident process documented |
| **ISO 27001 (future)** | Asset inventory, risk register, supplier review, documented procedures |

NeatSprint does not claim SOC 2 or ISO certification for v1.0. The documentation and controls are
built so certification work is an audit exercise, not a rebuild.

---

## 16. Verification Checklist (per release)

- [x] Isolation suite green; one manual cross-tenant probe performed
- [ ] Authz matrix covers 100% of protected routes (route-registration test)
- [x] Privacy deletion verified against storage (blob, key, embeddings)
- [x] Pending screenshots inaccessible to managers
- [x] Secret scan clean; SBOM generated; container scan no high/critical
- [ ] JWT/key rotation rehearsed in staging
- [x] Backup restore verified and documented
- [ ] Audit log immutability verified (attempted update fails)
- [ ] Incident contact list and runbook current
- [ ] Legal pages published and linked (M5)

---

## 17. Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-SEC-01 (Tenant check in Reports burndown — S1)**: In `neatsprint-reports`
  `GET /reports/burndown` (`src/neatsprint_reports/api/router.py:275`), `session.get(ReportSprintFact, sprint_id)`
  must verify `snapshot.tenant_id == principal.tenant_id` so a foreign `sprint_id` cannot leak
  sprint start/completion dates (`IMP-T01`).
- [ ] **IMP-SEC-02 (PostgreSQL RLS across all services — S2)**: Extend PostgreSQL Row-Level Security
  from Task and Team to Reports, Worklog, Monitoring and tenant-scoped IAM tables (`IMP-T02`).
- [ ] **IMP-SEC-03 (Web CSP for Google Identity Services & dynamic API/S3 origins — S2)**:
  `services/neatsprint-web/next.config.ts` currently blocks `https://accounts.google.com/gsi/client`
  in `script-src` and hardcodes `http://localhost:8000` / `http://localhost:9000`. Update the CSP
  to allow Google GIS when enabled, derive API/S3 origins from environment configuration, and
  migrate toward per-request CSP nonces (§10, `IMP-T04`).
- [ ] **IMP-SEC-04 (BFF CSRF Origin check & cookie prefix)**: Add explicit `Origin`/`Referer`
  validation on state-changing BFF routes (`/api/session/**`) and use `__Host-` cookie prefixes
  when running behind HTTPS in production (§10).
- [ ] **IMP-SEC-05 (Close remaining §16 release checklist items)**:
  1. Add an automated route-registration test asserting 100% of FastAPI routes declare a permission
     dependency or an explicit public allow-list entry (`IMP-T08`).
  2. Add an automated integration test asserting `UPDATE`/`DELETE` on `audit_log` fails via the DB
     trigger.
  3. Rehearse JWT key rotation (`two active kids`) on staging and record evidence.
  4. Render and link the legal documents (`legal/*.md`) in the web footer (`IMP-T10`).

---

**End of Security & Privacy Model**
