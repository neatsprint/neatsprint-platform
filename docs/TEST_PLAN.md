# NeatSprint — Test Plan

> **Status**: Approved v1.0 · **Version**: 1.0 · **Last updated**: 2026-11-21
> **Owner**: Laksiri Fernando (acceptance) · **Executor**: OpenCade (AI, QA)
> **Parent**: `MASTER_PLAN.md` · **Executed by**: `DEVELOPMENT_PLAN.md` tasks · **Requirements**: `SCOPE.md`

---

## 1. Objectives

1. Prove each requirement in `SCOPE.md` behaves as specified, including the negative cases.
2. Prove **tenant isolation** and **permission enforcement** cannot be bypassed.
3. Prove the **privacy promise**: deletion destroys image data and derived embeddings, and
   leaves only an auditable tombstone.
4. Prove **offline durability**: no time, screenshot or state is lost across disconnects.
5. Keep regressions out: every fixed defect ships with a failing-then-passing test.
6. Provide evidence for each milestone gate (G1–G6 in the master plan).

**Non-goals for MVP**: penetration test by a third party (scheduled post-MVP), full ASVS
Level 3, multi-region failover testing, load testing beyond the documented scale.

---

## 2. Test Levels & Ownership

| Level | Scope | Tooling | Runs |
| :--- | :--- | :--- | :--- |
| **Unit** | Pure domain logic, validators, policies, pure functions | pytest / Vitest / cargo test | Every commit (pre-push + CI) |
| **Integration** | Service + real Postgres/Redis/MinIO via containers | pytest + testcontainers | Every PR |
| **Contract** | OpenAPI schema conformance, client/server drift | schemathesis / dredd-style checks | Every PR |
| **Component (UI)** | Screens, components, states | Vitest + Testing Library + axe | Every PR |
| **E2E** | Critical user journeys across gateway and services | Playwright | Merge to `main`, nightly |
| **Desktop** | Agent behaviour, capture, offline, crypto | Rust tests + Playwright-for-Tauri + manual checklist | Nightly + release |
| **Performance** | Latency and throughput at target scale | k6 | Pre-release + nightly (reduced) |
| **Security** | Authz matrix, tenant isolation, injection, uploads | pytest + custom suites + ZAP baseline | Every PR (fast), pre-release (full) |
| **Accessibility** | WCAG 2.1 AA | axe-core + manual keyboard/screen-reader | Every PR (automated) + M4 manual |
| **UAT** | Acceptance criteria | Scripted manual session with Laksiri | Milestone gates |

---

## 3. Environments & Test Data

| Environment | Purpose | Data |
| :--- | :--- | :--- |
| **local** | Developer loop | Seeded demo tenant; ephemeral DB per test run |
| **ci** | Automated gates | Containers; deterministic factories, no network |
| **staging** | Pre-release verification, UAT | Anonymised seed + synthetic load data |
| **production** | Smoke only | Real data; read-only checks + synthetic tenant |

**Test data rules**

- Factories (not fixtures files) generate entities; every factory sets `tenant_id` explicitly.
- Two tenants always exist in integration tests: `tenant_a` and `tenant_b` — isolation tests use
  both. A helper `assert_cross_tenant_denied()` wraps the common pattern.
- Time is injected (`clock` dependency), never read directly from the system.
- UUIDs are deterministic in unit tests (factory sequence) and random UUIDv7 in integration.
- No real PII, no real screenshots of people; use generated patterns with a visible "TEST" mark.

---

## 4. Test Suites

| ID | Suite | Covers | Gate |
| :--- | :--- | :--- | :--- |
| TS-01 | Identity & session | FR-IAM-01…09, NFR-SEC | M1 |
| TS-02 | Authorisation & isolation | FR-RBAC-01…06, NFR-SEC-02 | M1, every PR |
| TS-03 | Work management | FR-PRJ-01…12, FR-TEM-01…04 | M2 |
| TS-04 | Time tracking | FR-WRK-01…08, NFR-REL-04 | M3 |
| TS-05 | Reports | FR-RPT-01…09 | M4 |
| TS-06 | Monitoring & privacy | FR-MON-01…10, NFR-SEC-06 | M3 |
| TS-07 | Web UI & accessibility | FR-WEB-01…06, NFR-UX-01 | M1–M4 |
| TS-08 | Desktop agent | FR-DSK-01…10, NFR-REL-03 | M3 |
| TS-09 | Chat / mobile / notifications | FR-CHT, FR-MOB, FR-NOT | P2 |
| TS-10 | AI guardrails | FR-AI-01…07 | P3 |
| TS-11 | Performance, resilience, ops | NFR-PERF, NFR-REL, NFR-MNT | M5 |

---

## 5. Key Test Cases

Format: ID · scenario · expected result. Full automation maps to these IDs in test names
(`def test_tc_sec_004_...`).

### 5.1 TS-01 Identity & Session

| ID | Scenario | Expected |
| :--- | :--- | :--- |
| TC-IAM-001 | Valid email/password login | 200, access + refresh issued, `last_login_at` updated |
| TC-IAM-002 | Wrong password ×5 | Lockout with generic message, rate limit engaged, audit entries |
| TC-IAM-003 | Login for deactivated user | 401, no token, event `auth.denied` |
| TC-IAM-004 | Refresh rotation | New refresh returned; old refresh rejected 401 |
| TC-IAM-005 | Refresh reuse | Entire session family revoked; audit `refresh_reuse_detected` |
| TC-IAM-006 | Logout then use access token | 401 via revocation check |
| TC-IAM-007 | Invite → accept → login | User in correct tenant, roles/teams applied |
| TC-IAM-008 | Expired invite | 410 with `invitation_expired`; resend works |
| TC-IAM-009 | Duplicate invitation | Single pending invite, second email not sent |
| TC-IAM-010 | Google login, unverified email domain | Rejected unless tenant allows domain auto-join |
| TC-IAM-011 | Password reset token reuse | Second use rejected |
| TC-IAM-012 | JWT signed with wrong key | Rejected by gateway and service |
| TC-IAM-013 | Expired JWT | 401 `token_expired` |
| TC-IAM-014 | JWT from another tenant, header spoofed | Denied; spoofed header stripped |
| TC-IAM-015 | Admin deactivates user mid-session | Next call 401; desktop receives suspend event |
| TC-IAM-016 | 20 users of one tenant log in and work concurrently | Each gets an independent session/token; no cross-user data |
| TC-IAM-017 | Invite an email already active in another tenant | `409 email_unavailable`, neutral copy, no tenant name or existence leak |
| TC-IAM-018 | Deactivate one of many users in a tenant | Only that user is blocked; all other sessions unaffected |

### 5.2 TS-02 Authorisation & Tenant Isolation (must pass on every PR)

| ID | Scenario | Expected |
| :--- | :--- | :--- |
| TC-SEC-001 | `VIEWER` attempts create item | 403 `permission_denied` with required permission |
| TC-SEC-002 | `MEMBER` reads another user's timesheet | 403 unless `work:log:view_team` |
| TC-SEC-003 | Manager grants `ADMIN` role | 403 privilege escalation blocked |
| TC-SEC-004 | Tenant A user requests Tenant B project by ID | 404 (not 403 — no existence leak) |
| TC-SEC-005 | Tenant A token with `X-Tenant-ID` of B | 403 tenant mismatch |
| TC-SEC-006 | List endpoint pagination across tenants | Only own tenant rows returned |
| TC-SEC-007 | Guessed UUID of foreign attachment | 404, no blob stream |
| TC-SEC-008 | Report query forced with foreign `team_id` | Empty/403, never data |
| TC-SEC-009 | Removed team member | Loses team-scoped visibility on next request |
| TC-SEC-010 | Custom role with unknown permission | 422 rejected |
| TC-SEC-011 | SQL injection in filter param | Parameterised; no error leak |
| TC-SEC-012 | Mass assignment of `tenant_id` in body | Ignored; server uses token tenant |
| TC-SEC-013 | Disabled module endpoint | 403 `module_disabled` |
| TC-SEC-014 | Direct DB connection attempt from another service (config test) | Credentials absent / denied |

### 5.3 TS-03 Work Management

| ID | Scenario | Expected |
| :--- | :--- | :--- |
| TC-PRJ-001 | Create project with duplicate key in tenant | 409 |
| TC-PRJ-002 | Same key in another tenant | 201 (keys are tenant-scoped) |
| TC-PRJ-003 | Archive project | Read-only, excluded from default list, still addressable |
| TC-PRJ-004 | Create item under archived project | 422 `project_archived` |
| TC-PRJ-005 | Illegal transition `TODO → DONE` | 422 `invalid_transition` |
| TC-PRJ-006 | Assign second user to item | 422 `single_assignee` |
| TC-PRJ-007 | Assign user not in project teams | 422 `assignee_not_eligible` |
| TC-PRJ-008 | 100 concurrent reorders | Unique ranks, stable order |
| TC-PRJ-009 | Start second active sprint | 409 |
| TC-PRJ-010 | Complete sprint twice | Second call idempotent, no duplicate history |
| TC-PRJ-011 | Carry-over to next sprint | Unfinished items moved, estimates preserved |
| TC-PRJ-012 | Comment edit history | Previous versions retrievable in history |
| TC-PRJ-013 | Delete comment | Soft-deleted; hidden from members, visible tombstone to admin audit |
| TC-PRJ-014 | Attachment 30 MB | 413 rejected |
| TC-PRJ-015 | Attachment wrong MIME disguised | Rejected by content sniffing |
| TC-PRJ-016 | Item key sequence under concurrency | No duplicates, no gaps beyond rolled-back txns |

### 5.4 TS-04 Time Tracking

| ID | Scenario | Expected |
| :--- | :--- | :--- |
| TC-WRK-001 | Start timer | Session open, `GET /work/current` returns it |
| TC-WRK-002 | Start second timer | 409 with current session payload |
| TC-WRK-003 | Stop timer | Duration matches monotonic elapsed (±1 s) |
| TC-WRK-004 | System clock moved back 1 h | No extra time credited |
| TC-WRK-005 | Idle 10 min with threshold 5 | Segment flagged; user accepts → time truncated |
| TC-WRK-006 | Idle segment discarded | Not counted in totals |
| TC-WRK-007 | Offline batch of 500 entries synced | All accepted; replay produces 0 duplicates |
| TC-WRK-008 | Clock skew on batch | Server clamps; anomaly flagged in audit |
| TC-WRK-009 | Manual entry overlapping timer | Warned/allowed per policy; totals correct |
| TC-WRK-010 | Timesheet totals | Sum equals raw entries to the second |
| TC-WRK-011 | CSV export without permission | 403 |
| TC-WRK-012 | Concurrent stop from desktop and mobile | Single closed session, other gets 409 |

### 5.5 TS-05 Reports

| ID | Scenario | Expected |
| :--- | :--- | :--- |
| TC-RPT-001 | Time by project reconciles | Matches sum of entries |
| TC-RPT-002 | Time by user restricted | Manager sees team only |
| TC-RPT-003 | Deleted screenshot time | Still counted in active time (policy) |
| TC-RPT-004 | Velocity uses completed scope only | Removed items excluded |
| TC-RPT-005 | Burndown daily points | Remaining = scope − done, monotone to zero |
| TC-RPT-006 | Aggregation mode, 3-person team | Individual rows hidden, totals shown |
| TC-RPT-007 | Report query for foreign tenant ids | Empty/403 |
| TC-RPT-008 | CSV export contents | Header + rows match UI values |
| TC-RPT-009 | PDF job async | `queued → running → done`, signed URL expires |
| TC-RPT-010 | Projector replay from scratch | Same results as incremental |
| TC-RPT-011 | Report latency at scale | < 5 s cached |

### 5.6 TS-06 Monitoring & Privacy

| ID | Scenario | Expected |
| :--- | :--- | :--- |
| TC-MON-001 | Timer running, interval 5–10 min | Captures within range, only while active |
| TC-MON-002 | Timer stopped | No further captures |
| TC-MON-003 | User deletes screenshot inside window | 204; blob gone; tombstone; audit row |
| TC-MON-004 | User deletes screenshot after window | 403 `window_closed` |
| TC-MON-005 | Manager requests deleted blob | 404; tombstone metadata only |
| TC-MON-006 | Manager requests pending (in-window) blob | 403 `not_yet_visible` |
| TC-MON-007 | Manager views visible screenshot | 200 + view audit entry |
| TC-MON-008 | Manager gallery listing | Deleted shown as "Deleted by user", no thumbnail |
| TC-MON-009 | Delete twice | Idempotent 204 |
| TC-MON-010 | Retention expiry job | Metadata + blob + embeddings removed |
| TC-MON-011 | Upload from revoked device | 401/403 |
| TC-MON-012 | Upload exceeding quota | 429 `quota_exceeded` |
| TC-MON-013 | Encrypted upload tampered | Decryption fails; rejected, no partial row |
| TC-MON-014 | Cross-tenant screenshot id | 404 |
| TC-MON-015 | Transparency log completeness | Every capture/delete appears for the owner |
| TC-MON-016 | Remote wipe command | Agent clears DB/tokens and exits, server records ack |

### 5.7 TS-07 Web UI & Accessibility

| ID | Scenario | Expected |
| :--- | :--- | :--- |
| TC-UI-001 | Keyboard-only sprint board move | Item moves with documented keys; focus preserved |
| TC-UI-002 | Axe scan on every route | 0 serious/critical violations |
| TC-UI-003 | Contrast check on all text tokens | ≥ 4.5:1 normal, ≥ 3:1 large |
| TC-UI-004 | Empty state for each list | Helpful copy + primary action |
| TC-UI-005 | API failure state | Error panel with retry, no white screen |
| TC-UI-006 | Slow network (Fast 3G) board load | Skeleton then content, no layout shift > 0.1 |
| TC-UI-007 | Dark mode field/board visibility | Tokens pass contrast |
| TC-UI-008 | Permission-hidden controls | Not rendered; direct API call still 403 |
| TC-UI-009 | Session expiry during edit | Redirect to login with return path; draft preserved |
| TC-UI-010 | 1280×720 and 1024×768 layouts | No horizontal scroll on primary flows |
| TC-UI-011 | Screen reader announces status changes | Live region for save/toast |
| TC-UI-012 | Reduced motion | Animations disabled |

### 5.8 TS-08 Desktop Agent

| ID | Scenario | Expected |
| :--- | :--- | :--- |
| TC-DSK-001 | First run + login | Device registered, key in OS keychain |
| TC-DSK-002 | Start timer from tray | Server session opened within 2 s |
| TC-DSK-003 | 4-hour offline session with screenshots | Queue grows, no loss, bounded disk |
| TC-DSK-004 | Reconnect after 4 h | All entries and screenshots synced, zero duplicates |
| TC-DSK-005 | Network flap during sync | Backoff, resume, no duplication |
| TC-DSK-006 | Kill process during capture | No corrupt DB; resume succeeds |
| TC-DSK-007 | Inspect SQLite file externally | Unreadable (encrypted) |
| TC-DSK-008 | Delete screenshot in review tray | Local file wiped (secure), deletion event queued |
| TC-DSK-009 | Window closes while pending | Screenshot auto-submits as pending (not visible until window ends) |
| TC-DSK-010 | Remote suspend | Capture pauses, indicator shows paused, UI locked |
| TC-DSK-011 | Remote revoke | Tokens cleared, login screen |
| TC-DSK-012 | Remote wipe | Local DB and files destroyed, app exits |
| TC-DSK-013 | Tampered updater payload | Signature rejected, no install |
| TC-DSK-014 | Version downgrade attempt | Rejected (monotonic) |
| TC-DSK-015 | Multi-monitor capture | Selected displays captured; no partial/black frames |
| TC-DSK-016 | Idle detection with no input 10 min | Timer pauses/prompts per policy |
| TC-DSK-017 | Token copied to another machine | Request signature mismatch; denied |
| TC-DSK-018 | 8-hour soak | CPU < 2% avg, RAM < 250 MB, no leak |

### 5.9 TS-09..TS-10 (deferred suites)

Defined when P2/P3 start. Baseline cases already reserved:

- TC-CHT-001…012 (auth on WebSocket, channel membership, history pagination, presence).
- TC-MOB-001…010 (biometrics, offline queue, push deep link, secure storage).
- TC-AI-001…015 (permission mirroring, deleted-screenshot exclusion, confirmation before write,
  audit completeness, prompt injection resistance, PII scrubbing).

### 5.10 TS-11 Performance, Resilience & Operations

| ID | Scenario | Expected |
| :--- | :--- | :--- |
| TC-PERF-001 | Read API mix @ 200 rps for 10 min | p95 < 300 ms, error < 0.1% |
| TC-PERF-002 | Write API mix @ 50 rps | p95 < 500 ms |
| TC-PERF-003 | 20 concurrent screenshot uploads | Accepted < 2 s each |
| TC-PERF-004 | Report for 250 users | < 5 s cached |
| TC-PERF-005 | Web LCP (Lighthouse, mid laptop) | < 2.5 s |
| TC-REL-001 | Kill task service | Gateway 502/503 JSON; auto-recovery; no data loss |
| TC-REL-002 | Redis outage | Auth still works via DB fallback (degraded), documented behaviour |
| TC-REL-003 | Postgres failover (managed) | App reconnects; < 60 s disruption |
| TC-REL-004 | Backup restore into clean env | Data and timestamps match; RTO recorded |
| TC-OPS-001 | Alert fires on induced 5xx | Notification received with runbook link |
| TC-OPS-002 | Log contains trace id | Correlates gateway → service → DB span |
| TC-OPS-003 | Health endpoints | `/healthz` 200 with DB down; `/readyz` 503 |

---

## 6. Security Testing Detail

### 6.1 Authorisation matrix automation

A generated test iterates **every** protected endpoint × every role × resource ownership
(own / same-team / other-team / other-tenant) and asserts the expected allow/deny from the
matrix in `SECURITY.md` §5.3. A new endpoint without a matrix entry fails the test — this is the
main defence against silent authz gaps.

### 6.2 Tenant isolation harness

```python
# tests/isolation/conftest.py (illustrative)
@pytest.mark.parametrize("endpoint", protected_get_endpoints())
def test_cross_tenant_read_is_404(client, tenant_a_auth, tenant_b_object, endpoint):
    response = client.get(endpoint.format(id=tenant_b_object.id), headers=tenant_a_auth)
    assert response.status_code in (403, 404)
    assert tenant_b_object.id not in response.text
```

Every mutating endpoint additionally asserts no row of tenant B changed.

### 6.3 Privacy verification

Deletion tests must inspect **storage**, not just the API:

1. Upload → confirm object exists in MinIO/S3.
2. Delete via API.
3. Assert `GET` object → 404/NoSuchKey.
4. Assert DB row `storage_path IS NULL`, `deleted_by_user = true`.
5. Assert AI embedding rows (when present) are gone.
6. Assert audit entry, and manager listing shows tombstone only.

### 6.4 Other security tests

- JWT tampering, `alg: none`, kid confusion, expired keys.
- Header injection (`X-Forwarded-For`, `X-Tenant-ID`, CRLF).
- File upload: polyglot files, zip bombs, path traversal in filenames.
- CSRF on cookie-based web routes; SameSite and Origin checks.
- Rate-limit bypass via header rotation.
- Dependency and container CVE scan (Trivy), secret scan (gitleaks).
- ZAP baseline against staging before release.

---

## 7. Entry & Exit Criteria

### Per pull request

- Entry: branch builds locally.
- Exit: lint, types, unit, integration, contract, fast security suite green; coverage not lower
  than target; no new high/critical scan findings.

### Per milestone

- Entry: all tasks in the milestone checked except this gate's evidence tasks.
- Exit: full suite green on `main`; milestone-specific suites (TS-0x) pass; manual checklist for
  that milestone completed; evidence attached to the AI message (test output, screenshots).

### Release (M5)

- Entry: SCOPE §8 items demonstrably pass in staging.
- Exit: load, security, restore and UAT evidence recorded; Laksiri signs acceptance; release notes
  and rollback procedure published.

---

## 8. Defect Management

| Severity | Definition | SLA |
| :--- | :--- | :--- |
| **S1 Critical** | Data loss, cross-tenant leak, auth bypass, privacy breach | Fix before any other work; hotfix release |
| **S2 High** | Core flow broken, no workaround | Fix in current milestone |
| **S3 Medium** | Broken with workaround, UX defect | Next milestone or backlog |
| **S4 Low** | Cosmetic, copy, minor polish | Backlog |

Rules:

- Every S1/S2 fix includes a regression test named after the defect.
- S1 during a milestone pauses feature work until a green regression test exists.
- Cross-tenant leak and privacy breach are **always** S1, regardless of exploitability.

Defect record fields: id, title, severity, environment, steps, expected/actual, affected
requirement IDs, test to add, fix commit.

---

## 9. Metrics & Reporting

| Metric | Target |
| :--- | :--- |
| Unit coverage (domain logic) | ≥ 80% |
| Permission-check coverage | 100% of protected endpoints |
| Flaky test rate | < 1% of runs |
| Defect leakage to UAT | 0 S1/S2 |
| E2E pass rate on `main` | ≥ 99% |
| Mean time to detect regression | Same CI run |

A milestone test report is appended to `agent/conversation.md` with: suites run, pass/fail counts,
coverage, open defects, and evidence links.

---

## 10. Traceability

| Requirement group | Suites | Milestone gate |
| :--- | :--- | :--- |
| FR-TEN, FR-IAM, FR-RBAC | TS-01, TS-02 | M1 |
| FR-PRJ, FR-TEM | TS-03 | M2 |
| FR-WRK, FR-DSK, FR-MON | TS-04, TS-06, TS-08 | M3 |
| FR-RPT, FR-WEB | TS-05, TS-07 | M4 |
| NFR-SEC, NFR-REL, NFR-PERF | TS-02, TS-11 | M5 |
| NFR-UX | TS-07 | M4 |
| FR-CHT, FR-MOB, FR-NOT | TS-09 | P2 |
| FR-AI | TS-10 | P3 |

---

## 11. Manual Test Checklists

Automation does not cover perception, physical devices or legal wording. These are executed at
gates and recorded with screenshots.

### M3 desktop checklist

- [ ] Install from MSI on a clean Windows 11 VM; tray appears; login succeeds
- [ ] Recording indicator visible and colour changes with state
- [ ] Toast appears at capture; no capture when timer stopped
- [ ] Review tray preview is sharp on a 150% DPI monitor
- [ ] Delete confirmation wording matches `UI_UX_DESIGN.md`
- [ ] Unplug network for 1 h: timer continues, queue grows, UI shows offline
- [ ] Reconnect: sync completes; server timesheet matches local
- [ ] Suspend/revoke/wipe commands take effect within 60 s
- [ ] Uninstall: local encrypted data removed or documented as retained

### M4 UX checklist

- [ ] First-run onboarding completes in < 3 minutes
- [ ] All destructive actions require confirmation with specific copy
- [ ] Every screen has a title, breadcrumb and back path
- [ ] Dark mode and light mode reviewed side by side
- [ ] 1024 px laptop layout reviewed for every primary screen
- [ ] Empty, loading, error and permission states reviewed for every list

### M5 acceptance checklist

- [ ] SCOPE §8 items 1–10 individually demonstrated
- [ ] Legal pages reachable from the footer and app menu
- [ ] Monitoring disclosure text reviewed for clarity by a non-technical reader

---

## 12. Test Plan Change Log

| Date | Change | Reason |
| :--- | :--- | :--- |
| 2026-11-21 | Plan v1 created | Initial planning cycle |
| 2026-11-24 | M5 verification executed (`LOAD_TEST.md`, `UAT.md`, `SBOM.md`, `ASVS_L2.md`) | v1.0.0–v1.0.2 release |

---

## 13. Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-TST-01 (Automated route-registration permission test — §6.1)**: Add a test in every
  FastAPI service that inspects `app.routes` and fails if any non-public endpoint lacks an explicit
  permission dependency (`IMP-T08`).
- [ ] **IMP-TST-02 (Expand cross-tenant probe to Reports & Monitoring — §6.2)**: Extend
  `scripts/security/cross_tenant_probe.py` to test foreign `sprint_id` on `GET /reports/burndown`
  (regression test for `IMP-T01`), foreign `export_id` on `GET /reports/exports/{id}/download`, and
  foreign `screenshot_id` / `session_id` / `device_id` on Monitoring endpoints (`IMP-T08`).
- [ ] **IMP-TST-03 (Playwright browser E2E suite in CI — §2)**: Add automated Playwright browser
  tests covering login, project/backlog item creation (`v1.0.1`), team member add/remove (`v1.0.2`),
  board transition, timesheet entry, screenshot deletion and report viewing, and wire `make e2e`
  into `web-ci.yml` (`IMP-T08`).
- [ ] **IMP-TST-04 (Audit log immutability & Lighthouse LCP checks)**: Add an automated test
  verifying the `trg_audit_no_update` PostgreSQL trigger rejects `UPDATE`/`DELETE` on `audit_log`,
  and add a Lighthouse CI check for `NFR-PERF-04` (LCP < 2.5 s, `TC-PERF-005`).
