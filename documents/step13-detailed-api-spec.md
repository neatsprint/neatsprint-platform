# NeatSprint – Step 13: Detailed API Specification

This document serves as the **Comprehensive API Catalog** for all NeatSprint microservices.
**Note**: For global standards (Headers, Error Codes, JSON Envelopes), refer to **[Step 12: API Contracts](step12-api-contracts.md)**.

---

## 1. IAM Service (`neatsprint-iam`)
**Base Path**: `/auth` and `/iam`

### 1.1. Authentication & Session
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/login` | Exchange credentials for Access/Refresh tokens. |
| `POST` | `/auth/refresh` | Obtain new Access Token using Refresh Token. |
| `POST` | `/auth/logout` | Revoke current Refresh Token. |
| `POST` | `/auth/social/{provider}` | OAuth2 callback (Google, GitHub, Microsoft). |

### 1.2. User Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/iam/users` | List users in tenant (Pagination). |
| `POST` | `/iam/users` | Create new user (Admin only). |
| `GET` | `/iam/users/{id}` | Get user details. |
| `PATCH` | `/iam/users/{id}` | Update user profile/status. |
| `POST` | `/iam/users/{id}/roles` | Assign roles to user. |

### 1.3. RBAC (Roles & Permissions)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/iam/roles` | List available roles. |
| `POST` | `/iam/roles` | Create custom role. |
| `GET` | `/iam/permissions` | List all system permissions. |

### 1.4. Invitations
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/iam/invitations` | Send email invite to new member. |
| `POST` | `/iam/invitations/accept` | Convert invite token to user account. |

---

## 2. Core Platform Service (`neatsprint-core`)
**Base Path**: `/core`

### 2.1. Tenant Lifecycle
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/core/tenants/current` | Get current tenant details. |
| `PATCH` | `/core/tenants/current` | Update settings/billing. |

### 2.2. Application Modules
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/core/applications` | List platform modules (Tasks, Chat, etc). |
| `GET` | `/core/tenant-applications` | List enabled modules for tenant. |
| `POST` | `/core/tenant-applications` | Enable/Disable a module. |

---

## 3. Task Service (`neatsprint-task`)
**Base Path**: `/tasks`

### 3.1. Projects
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/tasks/projects` | List projects. |
| `POST` | `/tasks/projects` | Create new project. |
| `GET` | `/tasks/projects/{id}` | Get project details. |
| `PUT` | `/tasks/projects/{id}` | Update project config. |

### 3.2. Sprints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/tasks/projects/{projectId}/sprints` | List sprints for project. |
| `POST` | `/tasks/sprints` | Create new sprint. |
| `POST` | `/tasks/sprints/{id}/start` | Start sprint. |
| `POST` | `/tasks/sprints/{id}/complete` | Complete sprint. |

### 3.3. Backlog Items (Stories/Tasks/Bugs)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/tasks/projects/{projectId}/backlog` | Get backlog items. |
| `POST` | `/tasks/backlog` | Create item. |
| `PATCH` | `/tasks/backlog/{id}` | Move item / Update status. |
| `POST` | `/tasks/backlog/{id}/assign` | Assign user to item. |

---

## 4. Team Service (`neatsprint-team`)
**Base Path**: `/teams`

### 4.1. Team Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/teams` | List teams. |
| `POST` | `/teams` | Create team. |
| `GET` | `/teams/{id}/members` | List members of a team. |
| `POST` | `/teams/{id}/members` | Add user to team. |
| `DELETE` | `/teams/{id}/members/{userId}` | Remove user from team. |

---

## 5. Worklog Service (`neatsprint-worklog`)
**Base Path**: `/work`

### 5.1. Time Tracking
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/work/start` | Start live timer for task. |
| `POST` | `/work/stop` | Stop current timer. |
| `GET` | `/work/current` | Get status of running timer. |
| `GET` | `/work/logs` | List history (filterable by date/user). |
| `POST` | `/work/logs` | Manual time entry log. |

---

## 6. Monitoring Service (`neatsprint-monitoring`)
**Base Path**: `/monitor`

### 6.1. Desktop Agent Telemetry
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/monitor/sessions/start` | Initialize monitoring session. |
| `POST` | `/monitor/sessions/heartbeat` | Send activity pulse (mouse/keyboard). |
| `POST` | `/monitor/screenshots` | Upload encrypted screenshot. |
| `DELETE` | `/monitor/screenshots/{id}` | User-initiated privacy delete. |

### 6.2. Compliance
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/monitor/reports/daily` | Get daily activity summary. |

---

## 7. Chat Service (`neatsprint-chat`)
**Base Path**: `/chat`

### 7.1. Messaging
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/chat/rooms` | List DM/Group channels. |
| `GET` | `/chat/rooms/{id}/messages` | Get message history. |
| `POST` | `/chat/rooms/{id}/messages` | Send new message. |
| `GET` | `/chat/ws` | **WebSocket** endpoint for real-time events. |

---

## 8. AI Service (`neatsprint-ai`)
**Base Path**: `/ai`

### 8.1. Assistant
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/ai/summaries/work-session` | Generate summary of worklogs. |
| `POST` | `/ai/assistant/query` | RAG-based query against project docs. |
| `GET` | `/ai/suggestions` | Suggested tasks/next-actions. |

---

**End of API Specification**
