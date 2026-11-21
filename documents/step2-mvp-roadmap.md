# NeatSprint – Step 2: Product Roadmap & Phasing

This document defines the **Product Release Schedule**. It enforces a strict **"Crawl, Walk, Run"** strategy to ensure steady delivery and prevent scope creep.

---

## 1. Phase 1: The Kernel (MVP)

**Goal**: A secure, stable, single-user tracking experience within a multi-tenant shell.
**Target Audience**: Freelancers, Small Agencies.

### 1.1. Core Platform
-   [x] **Tenancy**: Tenant creation, billing subscription limits.
-   [x] **IAM**: Email/Password Auth, Google OAuth, Basic RBAC (Owner/Member).
-   [x] **Projects**: CRUD Projects, Teams, Simple Backlog.

### 1.2. The Desktop Agent (Critical)
-   [x] **Tracking**: Start/Stop Timer, Idle Detection.
-   [x] **Monitoring**: Screenshot Capture (AES-256 Encrypted).
-   [x] **Offline Mode**: Local SQLCipher queue + Sync Engine.
-   [x] **Privacy**: "Delete Screenshot" tray action.

### 1.3. Reporting
-   [x] **Basic Views**: Time Sheets (Grid), Screenshot Gallery (Manager View).
-   [x] **Exports**: CSV Export of time logs.

**🛑 EXCLUDED from MVP**:
-   Chat / WebSockets.
-   Mobile App.
-   AI / Voice.

---

## 2. Phase 2: Collaboration (Growth)

**Goal**: Enabling teams to talk and manage work on-the-go.
**Target Audience**: Software Teams, Remote Workforce.

### 2.1. Mobile App (React Native)
-   [ ] **Scope**: Read-only Dashboards, Push Notifications, "Stop Timer" (Remote Control).
-   [ ] **Tech**: Shared TypeScript logic with Web.

### 2.2. Real-Time Comms
-   [ ] **Chat**: Team Channels, Direct Messages.
-   [ ] **Presence**: "Online/Offline" indicators based on Desktop Agent heartbeat.
-   [ ] **Notifications**: In-app alerts for "Task Assigned", "Mentioned".

---

## 3. Phase 3: Intelligence (Enterprise)

**Goal**: High-value automation and compliance features for large orgs.
**Target Audience**: Enterprises (>50 users), Regulated Industries.

### 3.1. AI Service
-   [ ] **NeatSprint Ask**: RAG-based project queries.
-   [ ] **Work Summaries**: Automated daily standup generation.
-   [ ] **Voice**: Push-to-talk commands.

### 3.2. Advanced Compliance
-   [ ] **Legal Hold**: Freezing retention policies.
-   [ ] **Custom Roles**: JSON-based permission composition.
-   [ ] **SIEM Integration**: Streaming audit logs to Datadog/Splunk.

---

## 4. Scope Freeze Protocol

To ensure MVP delivery, the following rules apply immediately:

1.  **The "Icebox" Rule**: Any new feature request is automatically moved to "Phase 2 Candidates". No exceptions.
2.  **The "Fix-Only" Rule**: Once Beta starts, development is restricted to Bug Fixes and Security Patches.
3.  **The "Data First" Rule**: No UI work begins until the underlying Schema (Step 12) and API Contract (Step 3) are final.

---

## 5. Success Criteria (MVP)

We are ready to launch Phase 1 when:

1.  **Security**: A penetration test confirms Tenant Isolation is unbreakable.
2.  **Privacy**: A user can delete a screenshot and verify it is gone from the Manager View physically.
3.  **Offline**: The Desktop Agent can track 4 hours of offline work and sync successfully without data loss.

---

**End of Roadmap**
