# OWASP ASVS L2 Self-Assessment

Date: 2026-11-24 · Scope: web app, gateway, IAM/Core/Task/Team/Worklog/Monitoring/Reports,
desktop agent deferred (ADR-019).

Legend: **PASS** implemented and verified; **PARTIAL** implemented with a documented gap;
**N/A** out of scope for the MVP surface.

| ASVS area | Control | Status | Evidence / gap |
| :--- | :--- | :--- | :--- |
| V1 Architecture | Threat model and trust boundaries | PASS | `SECURITY.md` §2, ADR-018/019 |
| V1 | Segmented services, no shared DB access | PASS | ADR-002, internal APIs |
| V2 Authentication | Password policy + Argon2id | PASS | IAM auth, tests |
| V2 | Uniform login errors, no user enumeration | PASS | IAM login |
| V2 | Brute-force protection | PASS | Gateway per-IP rate limit + Redis-backed 5/15 min lockout (PR #6) |
| V2 | Session rotation and revocation | PASS | Refresh rotation, session revoke |
| V3 Sessions | HttpOnly/SameSite/Secure cookies, no-store | PASS | BFF routes |
| V3 | Short access token TTL (15 min), refresh 7 days | PASS | IAM settings |
| V4 Access control | Server-side RBAC on every route | PASS | Permission dependencies |
| V4 | Tenant scope and 404 for foreign IDs | PASS | RLS + cross-tenant probe |
| V5 Input validation | Pydantic schemas, size/type limits | PASS | Services |
| V5 | File upload allow-list + size cap | PASS | Task/Monitoring |
| V5 | Malware scanning | PASS | ClamAV INSTREAM, fail closed; EICAR 422 verified |
| V6 Cryptography | TLS, Argon2id, AES-GCM envelope, Ed25519 plan | PARTIAL | Desktop key binding deferred |
| V7 Error handling | RFC 7807, no stack traces/PII | PASS | `neatsprint_lib.errors` |
| V8 Data protection | Screenshot encryption, deletion, no backups | PASS | Monitoring tests/live |
| V8 | Retention and tombstone audit | PASS | Jobs + audit |
| V9 Communications | HTTPS in production, security headers | PASS | Gateway/Next headers |
| V10 Malicious code | Lockfiles, CodeQL, Dependabot | PASS | Zero high/critical dependency alerts |
| V11 Business logic | Timer clamp, idempotent sync, one active session | PASS | Worklog tests |
| V12 Files | No path traversal in object keys | PASS | Tenant-prefixed keys |
| V13 API | OpenAPI generated, versioned contracts | PASS | Contracts repo |
| V14 Config | Secrets out of git, env examples | PASS | `.gitignore`, `.env.example` |
| V14 | Secret scanning | PASS | gitleaks in platform CI; clean on 70 commits |
| V14 | Dependency/container SBOM | PASS | Trivy 0.69.3, 0 high/critical; `docs/SBOM.md` |

## High/critical gaps to close before launch

1. ~~Upload malware scanning~~ — closed 2026-11-24 (ClamAV, fail closed, EICAR verified).
2. ~~Shared brute-force lockout~~ — closed 2026-11-24 (Redis counters, PR #6).
3. ~~Supply-chain gate~~ — closed 2026-11-24 (Trivy action 0.35.0, SBOMs published, all images clean).
4. **Desktop verification** — device binding, SQLCipher, updater signing (ADR-019 deferral).

No unmitigated high/critical issue was found in the web/backend surface during this review.
