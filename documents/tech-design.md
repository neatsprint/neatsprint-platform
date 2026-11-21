# NeatSprint – Technical Specification

## 1. System Overview

NeatSprint is a **multi-tenant SaaS platform** designed for agile task management, transparent work monitoring, and team collaboration. It follows a **microservices architecture** to ensure scalability, strict tenant isolation, and future extensibility for additional enterprise applications (e.g., ERP, APS).

### Key Architectural Pillars
- **Multi-Tenancy**: Logical isolation per tenant (`tenant_id`) enforced at Gateway and DB layers.
- **Privacy-First Monitoring**: Work tracking with user-controlled screenshot deletion and ethical guardrails.
- **Extensibility**: "Global Application" registry allowing tenants to subscribe to distinct apps.
- **Security**: Feature-based RBAC, JWT (RS256) auth, and device-bound sessions.
- **Global IDs**: **UUIDv7** (Time-Ordered) used universally for offline safety and DB performance.
- **Client-Diverse**: Native Desktop (Offline-capable), Mobile (On-the-go), and Web (Management) clients.

---

## 2. Microservice Architecture

The system is composed of **10 specialized microservices** plus a centralized API Gateway.

### 2.1. Infrastructure Services

| Service | Responsibility | Key Tech |
| :--- | :--- | :--- |
| **API Gateway** (`neatsprint-apigw`) | Single entry point, Rate Limiting, JWT Validation, Routing. | Nginx / Kong |
| **IAM Service** (`neatsprint-iam`) | Auth (OIDC/OAuth2), RBAC policy, User/Role mgmt. | FastAPI, RS256 |
| **Core Platform** (`neatsprint-core`) | Tenant lifecycle, Application registry, Subscription enforcement. | FastAPI |

### 2.2. Domain Services

| Service | Responsibility | Key Tables (Prefix) |
| :--- | :--- | :--- |
| **Task Service** (`neatsprint-task`) | Projects, Sprints, Backlogs, Task Assignments. | `projects`, `sprints`, `backlog_items` |
| **Team Service** (`neatsprint-team`) | Team grouping, Membership management. | `teams`, `team_members` |
| **Worklog Service** (`neatsprint-worklog`) | Time tracking, Timesheets, Activity logs. | `work_logs`, `time_entries` |
| **Monitoring** (`neatsprint-monitoring`) | Screenshot ingestion, Encryption, Privacy enforcement. | `monitoring_sessions`, `screenshots` |
| **Chat Service** (`neatsprint-chat`) | Real-time team chat, Daily scrum, WebSockets. | `team_messages` |
| **Reports** (`neatsprint-reports`) | Read-only analytics, PDF exports. | *(Read Replica Views)* |

### 2.3. Enterprise Services

| Service | Responsibility | Status |
| :--- | :--- | :--- |
| **AI Service** (`neatsprint-ai`) | Screenshot summaries, Voice assistant, Predictive planning. | **Enterprise Only** |

---

## 3. Data Architecture & Schemas

Each service owns its private database (Pattern: **Database-per-Service**). Direct cross-service DB access is forbidden. Data exchange occurs via REST APIs or Async Events.

> [!NOTE]
> **MVP Deployment Strategy**: To optimize infrastructure costs while maintaining strict isolation, services may share a **single physical database cluster** (e.g., RDS instance) but MUST use separate **logical databases** (e.g., `db_iam`, `db_task`). Code and Migrations must remain strictly separated.

### 3.1. IAM & Security Schema
- `users`: Global user identity (Tenant-scoped).
- `roles` & `permissions`: Feature-based definitions.
- `social_accounts`: Federated identity links.
- `invitations`: Secure onboarding tokens.

### 3.2. Core Schema
- `tenants`: Subscription and status.
- `applications`: Registry of available modules.
- `tenant_applications`: Feature flags per tenant.

### 3.3. Work & Project Schema
- `projects`: High-level containers.
- `sprints`: Time-boxed cycles.
- `backlog_items`: Polymorphic items (Task, Bug, Story).
- `screenshots`: Metadata only (blobs in S3). **Privacy Rule**: `deleted_by_user` flag soft-deletes the reference; blob is purged.

---

## 4. Security & Privacy Model

### 4.1. Authentication
- **Standard**: JWT (Access Token ~15m, Refresh Token ~7d).
- **Algorithm**: RS256 (Asymmetric signing).
- **Device Binding**: Tokens are bound to `device_id` to prevent session hijacking.

### 4.2. Authorization (RBAC)
- **Granularity**: Feature-level permissions (e.g., `TASK_CREATE`, `REPORT_VIEW`).
- **Scope**: All permissions are strictly scoped to the `tenant_id`.
- **Enforcement**:
  1. **Gateway**: Validates Token signature.
  2. **Service**: Validates Tenant + Permission claims.

### 4.3. Desktop Security
- **Anti-Tampering**: Binaries are code-signed.
- **Offline Mode**:
  - Captures and logs stored locally in **AES-256 Encrypted** SQLite.
  - Syncs automatically upon reconnection.
- **Privacy Window**: Users have a configurable window (e.g., 10m - 24h) to delete screenshots before locking.

---

## 5. Source Code Structure & Repositories

### 5.1. Workspace & Parent Repository Layout
The `neatsprint` repository acts as the **Orchestrator**. It contains global configuration and links to all service repositories as **Git Submodules**.

```text
neatsprint/                                                             # [git repo] Main Orchestrator
├── docker-compose.yml                                                  # Local development orchestration
├── .env.example                                                        # Global environment variables
├── documents/                                                          # Architecture & Scope documentation
│   ├── scope.md                                                        # Functional requirements
│   ├── step1-microservice-boundaries-and-responsibilities.md           # Microservices
│   ├── ...                                                             # Other documents
│   └── tech-design.md                                                  # Technical specification
├── legal/                                                              # Legal agreements (ToS, Privacy, EULA)
│   ├── ...                                                             # Legal documents
│   ├── README.md                                                       # Readme for Legal documents
├── services/                                                           # Directory container for submodules
│   ├── neatsprint-iam/                                                 # [git submodule] IAM Service
│   ├── neatsprint-task/                                                # [git submodule] Task Service
│   ├── ...                                                             # other service submodules
│   └── neatsprint-web/                                                 # [git submodule] Web Frontend
└── scripts/                                                            # Global utility scripts (setup, build)
```

### 5.2. Repository Strategy
The project uses a **Multi-Repo** approach with a central orchestrator.

| Repository | Purpose |
| :--- | :--- |
| `neatsprint` | **Orchestrator**: Docker Compose, Docs, Legal, Configs. |
| `neatsprint-mobile` | **Mobile App**: React Native / Flutter. |
| `neatsprint-desktop` | **Desktop Agent**: Electron / Tauri (Rust). |
| `neatsprint-web` | **Web App**: React / Next.js. |

### 5.3. Standard Directory Structure
All microservices (e.g., `neatsprint-iam`) must follow this standardized layout to ensure consistent tooling and onboarding.

```text
neatsprint-<service-name>/
├── src/
│   ├── api/                # API Routes & Controllers
│   ├── core/               # Business Logic & Domain Models
│   ├── db/                 # Database Models & Repositories
│   ├── services/           # External Service Integrations
│   └── utils/              # Shared Utilities
├── tests/                  # Unit & Integration Tests
├── migrations/             # Database Migration Scripts (Alembic/Flyway)
├── docker/                 # Service-specific Docker configs
├── .env.example            # Template for environment variables
├── Dockerfile              # Multi-stage build definition
├── pyproject.toml          # Dependency Management (Python)
└── README.md               # Service-specific documentation
```

---

## 6. Deployment & Infrastructure

- **Containerization**: Docker-native workflow.
- **Orchestration**:
  - *Dev*: Docker Compose.
  - *SaaS Prod*: Kubernetes (EKS/GKE).
- **Storage**:
  - Relational: PostgreSQL.
  - Object Store: S3 / MinIO (Screenshots).
  - Cache: Redis (Sessions, Throttling).

---

## 7. Roadmap & Phases

### Phase 1: MVP (Core Foundation)
- [x] Multi-tenancy & IAM.
- [x] Project & Task Management.
- [x] Basic Desktop Tracking (Time + Screenshots).
- [x] Manual Reports.

### Phase 2: Collaboration & Mobile
- [ ] Team Chat & Daily Scrum.
- [ ] Mobile App Beta.
- [ ] Notification System.

### Phase 3: Enterprise AI
- [ ] AI Summary of work logs.
- [ ] Predictive Sprint Velocity.
- [ ] Voice Assistant.

---

**End of Technical Specification**
