# NeatSprint – Agile Task Management Platform

![License: AGPLv3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Status](https://img.shields.io/badge/status-active-success)

**NeatSprint** is a **Commercial Open Source** agile task management platform. It combines a modern Web UI, a secure Desktop Agent for time tracking, Mobile apps and an AI native agentic system into a cohesive suite for teams and enterprises.

---

## ⚡ Key Features

-   **Multi-Tenant SaaS**: Built for isolation and scale (Tenants, Plans, Billing).
-   **Privacy-First Monitoring**: Desktop agent with "Delete Screenshot" privacy window.
-   **Enterprise Ready**: RBAC, Audit Logs, and GDPR Compliance out of the box.
-   **Open Source Core**: Licensed under **AGPLv3**, ensuring freedom for self-hosters.

---

## 🏗️ Architecture & Services

NeatSprint follows a **Microservices Architecture**.

| Service | Port | Description |
| :--- | :--- | :--- |
| **Frontend (Web)** | `3000` | React/Next.js Web Interface |
| **API Gateway** | `8000` | **Entry Point** (Traefik/Nginx) |
| **IAM Service** | `8001` | Auth, Users, Roles |
| **Core Service** | `8002` | Tenants, Billing, Apps |
| **Task Service** | `8003` | Projects, Sprints, Backlogs |
| **Team Service** | `8004` | Team Management |
| **Worklog Service** | `8005` | Time Tracking |
| **Monitoring** | `8006` | Screenshots & Privacy |
| **Chat Service** | `8007` | Real-time Communication |
| **Reports** | `8008` | Analytics & Exports |
| **AI Service** | `8009` | Summarization & Process Automation |

---

## 📚 Documentation Map

Our architecture is fully documented in the `documents/` directory.

### 🏛️ Foundation
-   **[Scope & User Stories](documents/scope.md)**: The functional requirements.
-   **[Technical Design](documents/tech-design.md)**: High-level system architecture.
-   **[Step 1: Master Diagram](documents/step1-neatsprint-full-architecture-diagram.md)**: The big picture.
-   **[Step 2: Roadmap](documents/step2-mvp-roadmap.md)**: Product phases (MVP vs Enterprise).

### 🧱 Core Architecture
-   **[Step 3: Microservices](documents/step3-microservice-boundaries-and-responsibilities.md)**: Service boundaries.
-   **[Step 4: API Gateway](documents/step4-api-gateway-architecture.md)**: Routing & Security.
-   **[Step 5: CI/CD](documents/step5-deployment-and-cicd-architecture.md)**: Deployment pipelines.

### 💾 Data & Security
-   **[Step 6: ER Diagrams](documents/step6-er-diagrams.md)**: Visual data models.
-   **[Step 7: Schemas](documents/step7-neatsprint-database-schemas.md)**: SQL Definitions.
-   **[Step 8: Security Model](documents/step8-security-and-privacy-model.md)**: Encryption & Privacy.
-   **[Step 9: Auth Flow](documents/step9-authorization-enforcement-flow.md)**: JWT & Enforcement.
-   **[Step 10: RBAC](documents/step10-rbac-definitions.md)**: Roles & Permissions.
-   **[Step 11: Retention](documents/step11-data-retention-policy.md)**: GDPR & Data Lifecycle.

### 🔌 API & Connectivity
-   **[Step 12: API Contracts](documents/step12-api-contracts.md)**: Global standards (JSON, Errors).
-   **[Step 13: Endpoints](documents/step13-detailed-api-spec.md)**: Detailed API Reference.
-   **[Step 14: E2E Flows](documents/step14-end-to-end-flows.md)**: Sequence Diagrams (Login, Upload).

### 🖥️ Clients
-   **[Step 15: Desktop Arch](documents/step15-desktop-app-architecture.md)**: Tauri/Rust Agent.
-   **[Step 16: Desktop Security](documents/step16-desktop-agent-security-and-offline-design.md)**: Offline & Anti-Tamper.
-   **[Step 17: Mobile Arch](documents/step17-mobile-app-architecture.md)**: React Native App.
-   **[Step 18: Web Arch](documents/step18-web-app-architecture.md)**: React Dashboard.

### 🧠 Advanced Features
-   **[Step19: Reports](documents/step19-reports-architecture.md)**: Reporting Engine.
-   **[Step 20: Report Specs](documents/step20-reports-functional-specs.md)**: Metric Definitions.
-   **[Step 21: AI Arch](documents/step21-ai-architecture.md)**: RAG Pipeline.
-   **[Step 22: AI Specs](documents/step22-ai-functional-specs.md)**: Standard Prompts & Rules.

---

## ⚖️ Legal & Licensing

NeatSprint uses a **Commercial Open Source** model.

-   **Source Code**: Licensed under **[AGPLv3](LICENSE)**. Free for self-hosting.
-   **Hosted Service**: Usage of our Cloud is governed by the **[Terms of Service](legal/tos.md)**.

See the **[Legal Directory](legal/README.md)** for details on Privacy, EULAs, and Trademarks.

---

## 🚀 Getting Started

### Prerequisites
-   Docker & Docker Compose

### Fast Launch
```bash
# 1. Clone
git clone https://github.com/neatsprint/neatsprint.git
cd neatsprint

# 2. Init Submodules
git submodule update --init --recursive

# 3. Start
docker-compose up -d
```
Access the **Web UI** at `http://localhost:3000`.

---

**NeatSprint** – *Simplify Agile.*
