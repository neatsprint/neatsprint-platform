# NeatSprint – Step 8: Security & Privacy Model

This document defines the comprehensive security architecture and privacy enforcements for the platform.

---

## 1. Authentication & Identity

### 1.1. Core Authentication
-   **Method**: RS256 Signed JWTs (Access & Refresh Tokens).
-   **Identity Provider**: `neatsprint-iam` (Internal) or Google/Workspace (OIDC).
-   **Session Management**:
    -   **Access Token**: Short-lived (15 min).
    -   **Refresh Token**: Long-lived (7 days), strictly rotated reuse detection.

### 1.2. Device Binding (Anti-Hijacking)
To prevent token theft/replay, every session is cryptographically bound to a specific device.
-   **Mechanism**: Login request sends a `device_id` (Hardware Fingerprint Hash).
-   **Enforcement**: The `device_id` is embedded in the JWT claim.
-   **Validation**: Every API request header (`X-Device-ID`) must match the token claim. Mismatch = Immediate Revocation.

---

## 2. Multi-Tenancy & Authorization

### 2.1. Isolation Strategy
-   **Logical Separation**: Enforced via `tenant_id` column in every table (See Step 12).
-   **API Enforcement**: Gateway rejects any request missing `X-Tenant-ID`.
-   **Data Leakage Prevention**: ORM layer automatically applies `WHERE tenant_id = ?` to all queries.

### 2.2. Role-Based Access Control (RBAC)
-   **Granularity**: Feature-level permissions (e.g., `TASK_CREATE`, `REPORT_VIEW`).
-   **Evaluation**: `Subject (User) -> Role -> Permission -> Application (Feature)`.
-   **Audit**: Every permission change is logged to an immutable audit trail.

---

## 3. Desktop Security (Offline & Monitoring)

### 3.1. Local Data Protection
The Desktop Agent functions offline. Sensitive data must be secured on the user's endpoint.
-   **Storage**: SQLite database.
-   **Encryption**: **SQLCipher** (AES-256) used for the entire database file.
-   **Key Management**: The decryption key is derived from the User's credentials + System Entropy (never stored plain).

### 3.2. Anti-Tampering
-   **Code Signing**: All binaries signed by valid certificates (Apple Notarization / Windows Authenticode).
-   **Process Integrity**: The agent monitors its own process memory for injection attempts.

---

## 4. Privacy & Monitoring Ethics

NeatSprint enforces a "Privacy-First" approach to employee monitoring.

### 4.1. The "Deletion Window" Design
Users have an absolute right to review and delete screenshots before they are finalized.
1.  **Capture**: Agent takes screenshot -> Encrypts locally -> Stores in "Pending Path".
2.  **Grace Period**: Configurable window (e.g., 24 hours). User can view/delete these locally.
3.  **Sync/Commit**:
    -   *If Deleted*: The blob is wiped. A "Deletion Event" (metadata only) is sent to server.
    -   *If Approved (or Timeout)*: Encrypted blob is uploaded to S3.

### 4.2. Manager/AI Visibility
-   **Deleted Screenshots**: **NEVER** visible. Neither Manager nor AI can access the pixel data. They only see "Screenshot Deleted by User at 10:00 AM".
-   **Encryption**: Screenshots are encrypted client-side. The server holds keys but strictly logs access.

---

## 5. Enterprise AI Guardrails

The AI Service (`neatsprint-ai`) is powerful but strictly boxed.

### 5.1. Data Barriers
-   **No Private Training**: Customer data is **NEVER** used to train the base foundation models.
-   **RAG Only**: AI operates on Retrieval-Augmented Generation context only.

### 5.2. Access Control
-   **Service Account**: AI runs as `ai_agent` service user.
-   **Scope**: It inherits the RBAC of the *requesting user*. It cannot "see" things the user cannot see.
-   **Sanitization**: PII (Personally Identifiable Information) scrubbed before context injection.

---

## 6. Infrastructure Security

-   **TLS**: 1.3 mandated for all transit.
-   **Secrets**: Managed via Vault / AWS Secrets Manager (No `.env` in images).
-   **Container Security**:
    -   Rootless containers.
    -   Read-only root filesystems where possible.
    -   Regular image scanning (Trivy).

---

## 7. Compliance (GDPR/CCPA)

-   **Right to Forget**: `hard_delete` API cascades through UUIDv7 references.
-   **Export**: Full JSON export of user lifecycle data available via `neatsprint-reports`.
-   **Processors**: Sub-processors (e.g., Email provider) listed in Legal documents.

---

**End of Security Model**
