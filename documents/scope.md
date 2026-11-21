# NeatSprint – Scope of the System

## 1. Core Principles

- **Multi-tenancy**
  - **Strict Isolation**: One user belongs to **one tenant**. Data is logically isolated.
  - **Global Application Registry**: Applications are global entities; multiple tenants subscribe to and use the same application.
  - **Tenant-Application Mapping**: The `tenant_application` relationship governs access.

- **Role-Based Access Control (RBAC)**
  - **Tenant-Scoped Roles**: Roles exist only within the context of a tenant.
  - **Feature-Based Permissions**: Roles are assigned specific **app functions/features** (e.g., `backlog.read`, `sprint.create`) rather than generic access.
  - **Multi-Role Support**: Users can hold **multiple roles** (via `role_user`), merging permissions additively.

- **Extensibility & Scalability**
  - **Microservices Architecture**: Core platform, IAM, and applications are separated for independent scaling.
  - **Application Agnostic Core**: The system is designed to support future applications (ERP, APS, Production Planning) without modifying the core tenant/auth architecture.

---

## 2. Application Features

### 2.1. Projects & Backlogs
- **Projects**: Central container for work; maintains project metadata and settings.
- **Project Backlog**: Unified list of all work items (Tasks, Issues, Suggestions, Bugs).
- **Sprints**: Time-boxed iterations for agile delivery.
- **Sprint Backlog**: Subset of items committed to a specific sprint.

### 2.2. Teams & Users
- **Teams**:
  - Groups of tenant users.
  - Can be assigned to **multiple projects**.
  - A project team helps filter views and context (chat, reports).
- **Users**:
  - Belong to a single tenant but can join **multiple teams**.
  - Can work across **multiple projects**.
- **Assignment Logic**:
  - **Backlog Items**: Assigned to **one user** only (ownership principle).
  - **Timing**: Assignment typically happens when moving items to a Sprint, but can occur earlier.
  - **Project Context**: Items must belong to a project upon creation.

### 2.3. Identity & Onboarding
- **Invitations**: Authorized users invite others via email.
- **Registration**: Invitees register and are automatically linked to the tenant and initial team.
- **Social Login**: Support for Google and Corporate Email (Google Workspace) via OAuth2.

---

## 3. Work Tracking & Monitoring

### 3.1. Time & Task Tracking
- **Manual Logging**: Users can manually log time entries with comments.
- **Desktop Timer**: Real-time start/stop tracking linked to specific tasks.
- **Task completion**: Explicit action to mark tasks as finished and finalize time logs.

### 3.2. Privacy-First Work Monitoring
- **Random Screenshots**: Captured at random intervals *only* while the timer is running.
- **User Agency**:
  - Users can **view their own screenshots**.
  - Users can **delete screenshots** within a configurable retention window (e.g., 24 hours).
- **Manager View**:
  - Managers see the *presence* of a deleted screenshot (for audit) but **cannot view the content**.
  - Active screenshots are visible to managers for performance review.
- **Audit**: Deletion events are logged to prevent abuse of the privacy feature.

---

## 4. Communication & Collaboration

- **Team Chat**:
  - Persistent, global chat channel per Project Team.
  - Real-time messaging (WebSockets).
- **Daily Scrum Support**: Integrated flow for daily status updates.
- **Platform Awareness**: Icons indicate user device (Web, Desktop, Mobile) during chat.

---

## 5. Reports & Analytics

- **Productivity Reports**: Task completion rates, hours logged (per project/sprint/user).
- **Monitoring Summaries**: Activity levels, screenshot logs, and time validation.
- **Agile Metrics**: Sprint velocity, backlog burndown.
- **Audit Reports**: Activity logs including screenshot deletions and permission changes.

---

## 6. Mobile App

*Focused on "On-the-Go" productivity.*
- **View**: Assigned projects, tasks, and notifications.
- **Action**: Log manual work time, update task status.
- **Collaborate**: Participate in team chat.
- **Manage**: Limited administrative actions (if role permits).

---

## 7. Desktop App

*The primary tool for reliable work tracking.*

### 7.1. Core Features
- **Smart Tracking**: Tray integration for start/stop, idle detection.
- **Collaboration**: Full access to team chat and task boards.
- **Offline Support**:
  - Continues tracking and capturing screenshots when offline.
  - Queues data locally (encrypted) and syncs automatically when connection is restored.

### 7.2. Security & Trust
- **Device Binding**: Tokens are bound to the specific device.
- **Encrypted Local Storage**: AES-256 encryption for cached data and screenshots.
- **Anti-Tampering**:
  - Signed binaries.
  - Integrity checks on startup.
  - Server-side heartbeat monitoring to detect disabled agents.

---

## 8. AI Features (Enterprise Plan)

*Assistive intelligence with strict guardrails.*

### 8.1. Capabilities
- **Work Summary**: AI analyzes non-deleted screenshots to timestamp activities and summarize work.
- **AI Assistant**: Chat/Voice interface to answer project questions ("What is due today?").
- **Backlog Assistant**: Suggests tasks, refines descriptions, and helps estimate effort.
- **Voice Interactions**: Push-to-talk voice commands for hands-free updates.

### 8.2. Guardrails & Safety
- **Authorization**: AI inherits the user's exact RBAC permissions. It cannot see or do what the user cannot.
- **Privacy Barrier**: **Deleted screenshots are never processed** by the AI.
- **Action Confirmation**: AI cannot mutate data (create/delete tasks) without explicit user confirmation.
- **Transparency**: All AI actions and data access are logged for audit.

---

## 9. Integrations

- **REST API**: Comprehensive, documented API for custom extensions.
- **Turnkey Integrations**:
  - **GitHub**: Link commits/PRs to tasks.
  - **Gmail**: Notifications and task creation from email.
- **Future**: Connectors for ERP/Financial systems.

---

## 10. Non-Functional Requirements

### 10.1. Security
- **Authentication**: JWT (Access + Refresh tokens), OAuth2 for SSO.
- **Authorization**: Fine-grained, API-level enforcement of RBAC.
- **Data Protection**: Encryption in transit (TLS 1.3) and at rest (DB & Object Storage).

### 10.2. Privacy & Compliance
- **GDPR Alignment**: Right to erasure (screenshot deletion), data retention policies.
- **Data Retention**: Configurable policies for screenshot auto-expiry and log retention.
- **Ethical Monitoring**: No hidden surveillance; users are always aware when tracking is active.

### 10.3. Reliability
- **Offline First**: Desktop app handles network interruptions gracefully.
- **Rate Limiting**: API Gateway protects against abuse.

---

## 11. Technical & Database Scope

- **Database Optimized Schema**:
  - **Core**: `tenant`, `user`, `role`, `application`, `tenant_application`.
  - **Work**: `project`, `team`, `sprint`, `backlog_item`, `task_assignment`.
  - **Tracking**: `time_entry`, `screenshot`, `activity_log`.
  - **Chat**: `chat_channel`, `chat_message`.
- **Infrastructure**: Containerized (Docker), ready for orchestration (K8s).

---

**End of Scope**
