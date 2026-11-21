# NeatSprint – Step 6: Database ER Diagrams

This document visualizes the data architecture.
**Critical Rule**: These diagrams represent **Logical Schemas**. Each Service owns its own database. Cross-service relationships (e.g., `user_id` in Task Service) are **Logical References** (UUIDv7), not Foreign Keys.

---

## 1. IAM Service (`neatsprint-iam`)

**Owner**: Identity & Access Management  
**Scope**: Users, Roles, and Auth.

```mermaid
erDiagram
    TENANT ||--|{ USER : "owns"
    TENANT ||--|{ ROLE : "defines"
    
    USER ||--o{ USER_CREDENTIALS : "has"
    USER ||--o{ SOCIAL_ACCOUNT : "has"
    USER ||--|{ USER_ROLE : "assigned"
    
    ROLE ||--|{ USER_ROLE : "assigned"
    ROLE ||--|{ ROLE_PERMISSION : "has"
    PERMISSION ||--|{ ROLE_PERMISSION : "granted"
    
    TENANT ||--o{ INVITATION : "issues"

    USER {
        uuid id PK
        uuid tenant_id FK
        string email
        string status
        timestamp created_at
        timestamp updated_at
    }
    ROLE {
        uuid id PK
        string name
        boolean is_system
        timestamp created_at
        timestamp updated_at
        uuid created_by "Logical Ref"
        uuid updated_by "Logical Ref"
    }
    PERMISSION {
        uuid id PK
        string feature_code
        string action
    }
    INVITATION {
        uuid id PK
        string email
        string token
        timestamp expires_at
    }
```

---

## 2. Core Platform Service (`neatsprint-core`)

**Owner**: Tenant Lifecycle & Billing  
**Scope**: Tenants, Applications, Features.

```mermaid
erDiagram
    TENANT ||--|{ TENANT_APPLICATION : "subscribes"
    APPLICATION ||--|{ TENANT_APPLICATION : "enabled_for"
    APPLICATION ||--|{ APPLICATION_FEATURE : "contains"

    TENANT {
        uuid id PK
        string name
        string plan
        timestamp created_at
        timestamp updated_at
        uuid created_by "Logical Ref"
        uuid updated_by "Logical Ref"
    }
    APPLICATION {
        uuid id PK
        string code "e.g. TASK, MONITORING"
        string name
    }
    TENANT_APPLICATION {
        uuid tenant_id PK, FK
        uuid application_id PK, FK
        boolean enabled
    }
```

---

## 3. Task Service (`neatsprint-task`)

**Owner**: Project Management  
**Scope**: Projects, Backlogs, Sprints.

```mermaid
erDiagram
    PROJECT ||--o{ BACKLOG_ITEM : "contains"
    PROJECT ||--o{ SPRINT : "has"
    PROJECT ||--o{ PROJECT_ASSIGNMENT : "assigned"
    
    SPRINT ||--|{ SPRINT_BACKLOG : "includes"
    BACKLOG_ITEM ||--|{ SPRINT_BACKLOG : "committed"
    
    BACKLOG_ITEM ||--o{ TASK_ASSIGNMENT : "assigned_to"

    PROJECT {
        uuid id PK
        uuid tenant_id
        string name
        timestamp created_at
        timestamp updated_at
        uuid created_by "Logical Ref"
        uuid updated_by "Logical Ref"
    }
    BACKLOG_ITEM {
        uuid id PK
        string type "TASK/BUG"
        string title
        string title
        uuid assignee_user_id "Logical Ref"
        timestamp created_at
        timestamp updated_at
        uuid created_by "Logical Ref"
        uuid updated_by "Logical Ref"
    }
    SPRINT {
        uuid id PK
        string name
        date start_date
        date start_date
        date end_date
        timestamp created_at
        timestamp updated_at
        uuid created_by "Logical Ref"
        uuid updated_by "Logical Ref"
    }
    PROJECT_ASSIGNMENT {
        uuid project_id PK, FK
        uuid team_id "Logical Ref"
        uuid user_id "Logical Ref"
    }
```

---

## 4. Team Service (`neatsprint-team`)

**Owner**: Organizational Structure  
**Scope**: Groups of users.

```mermaid
erDiagram
    TEAM ||--|{ TEAM_MEMBER : "has"

    TEAM {
        uuid id PK
        uuid tenant_id
        string name
        timestamp created_at
        timestamp updated_at
        uuid created_by "Logical Ref"
        uuid updated_by "Logical Ref"
    }
    TEAM_MEMBER {
        uuid team_id PK, FK
        uuid user_id PK "Logical Ref"
        timestamp joined_at
    }
```

---

## 5. Worklog Service (`neatsprint-worklog`)

**Owner**: Time Tracking  
**Scope**: Time entries independently of task state.

```mermaid
erDiagram
    WORK_LOG {
        uuid id PK
        uuid user_id "Logical Ref"
        uuid backlog_item_id "Logical Ref"
        timestamp start_time
        timestamp end_time
        int total_minutes
        int total_minutes
        string comment
        timestamp created_at
        timestamp updated_at
        uuid created_by "Logical Ref"
        uuid updated_by "Logical Ref"
    }
```

---

## 6. Monitoring Service (`neatsprint-monitoring`)

**Owner**: Privacy & Compliance  
**Scope**: Screenshots and audit trails.

```mermaid
erDiagram
    MONITORING_SESSION ||--o{ SCREENSHOT : "captures"

    MONITORING_SESSION {
        uuid id PK
        uuid user_id "Logical Ref"
        uuid backlog_item_id "Logical Ref"
        timestamp started_at
    }
    SCREENSHOT {
        uuid id PK
        uuid session_id FK
        string storage_path "Encrypted"
        boolean deleted_by_user
        timestamp deletion_deadline
    }
```

---

## 7. Chat Service (`neatsprint-chat`)

**Owner**: Real-time Comms  
**Scope**: Ephemeral and persistent messages.

```mermaid
erDiagram
    TEAM_MESSAGES {
        uuid id PK
        uuid team_id "Logical Ref"
        uuid user_id "Logical Ref"
        text message
        timestamp created_at
    }
```

---

## 8. Enterprise AI (`neatsprint-ai`)

**Owner**: Intelligence  
**Scope**: Summaries and cache.

```mermaid
erDiagram
    AI_SUMMARY {
        uuid id PK
        uuid session_id "Logical Ref"
        text summary
        timestamp created_at
    }
```

---

## Summary of Reference Types

| Reference Type | Example | Description |
| :--- | :--- | :--- |
| **Physical FK** | `backlog_item_id` in `SPRINT_BACKLOG` | Enforced by Database Constraint. Both tables live in the same DB. |
| **Logical Ref** | `user_id` in `TASK_ASSIGNMENT` | a **UUIDv7** string. Application checks validity against IAM Service API. No DB Constraint. |