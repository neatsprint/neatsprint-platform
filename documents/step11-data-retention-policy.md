# NeatSprint – Step 11: Data Retention & Policy

This document defines the **Technical Data Lifecycle Policies**. It translates legal requirements into system configurations (S3 Rules, Database TTLs, and Cron Jobs).

---

## 1. Data Classification

All data is categorized into tiers to determine its lifecycle and protection level.

| Tier | Category | Description | Storage | Sensitivity |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **Identity & Audit** | User PII, Login Logs, Access Audits. | Primary DB, Cold Archive | High |
| **Tier 2** | **Operational** | Projects, Tasks, Active Worklogs. | Primary DB | Medium |
| **Tier 3** | **Ephemeral** | Screenshots, AI Embeddings, Cache. | S3, Redis, Vector DB | **Very High** |

---

## 2. Retention Schedules (TTL)

These rules are enforced automatically by infrastructure policies.

### 2.1. Screenshot Lifecycle (Tier 3)
-   **Default**: 30 Days.
-   **Mechanism**: S3 Lifecycle Rule on `s3://neatsprint-screenshots/`.
    -   `Day 1-30`: Standard Class (Instant Access).
    -   `Day 31`: **Expire / Hard Delete**.
-   **Configurable**: Tenants can opt for shorter (e.g., 7 days) policies, enforced by a daily cleanup job.

### 2.2. Audit Logs (Tier 1)
-   **Default**: 1 Year.
-   **Mechanism**: Database Partitioning by Month.
    -   `Month 13`: Drop old partition (`ALTER TABLE audit_logs DROP PARTITION ...`).
-   **Archive**: Before dropping, logs are dumped to `s3://neatsprint-audit-archive/` (Glacier) for 7 years (Enterprise Plan).

### 2.3. Deleted Items (Soft Deletion)
-   **Scope**: Tasks, Projects, Comments.
-   **Mechanism**: `deleted_at` timestamp.
-   **Purge**: A `garbage_collector` job runs nightly.
    -   `WHERE deleted_at < NOW() - INTERVAL '30 DAYS'`: Hard Delete row.

---

## 3. Right to Erasure (GDPR Implementation)

When a user requests deletion, we follow an **Anonymization Strategy** to preserve business analytics while protecting privacy.

### 3.1. The "Forget User" Workflow
Triggered by IAM Event: `USER_DELETE_REQUEST`.

1.  **Identity Scrub (PII)**:
    -   `users.name` -> "Deleted User".
    -   `users.email` -> `deleted_{uuid}@neatsprint-void.com`.
    -   `users.avatar_url` -> `NULL`.
    -   `auth_methods` -> **DELETE** (Remove password hashes, social links).

2.  **Work History (Anonymization)**:
    -   `work_logs` are **KEPT** (to maintain Project Cost calculations).
    -   Why? Deleting worklogs would break the "Total Project Hours" report for the employer.
    -   Since the User ID is anonymized, the work logs are no longer personally updateable.

3.  **Surveillance Data (Hard Delete)**:
    -   `screenshots` (Entries): **DELETE**.
    -   `S3 Objects` (Images): **DELETE** immediately.
    -   **AI Embeddings**: **DELETE** from Vector DB.

---

## 4. Legal Hold Protocol

During litigation, normal retention rules must be suspended.

-   **Mechanism**: A `legal_hold = true` flag on the Tenant or User record.
-   **Effect**:
    -   S3 Lifecycle Rules: **Disabled** for that prefix.
    -   Garbage Collector: **Skips** that Tenant ID.
    -   User Deletion: **Blocked** API response.

---

## 5. Security of Deleted Data

-   **Crypto-Shredding**: For highly sensitive fields (e.g., Auth Tokens), we delete the encryption encryption key associated with that record (if per-row keys are used), rendering the data mathematically unrecoverable even if the bytes remain on disk.
-   **Backup Expiry**: Database backups are retained for 30 days. Deleted data naturally "falls out" of backups as old snapshots expire.

---

**End of Data Retention Policy**