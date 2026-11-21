# NeatSprint – Step 10: RBAC Definitions & Matrix

This document defines the **Technical RBAC Specification**. It maps high-level Roles to low-level **Permission Strings** used by the Authorization Enforcement system defined in **[Step 9](step9-authorization-enforcement-flow.md)**.

---

## 1. Permission Taxonomy (`resource:action`)

All permissions follow the format `domain:resource:action`.

### 1.1. Core Domain
| Permission String | Description |
| :--- | :--- |
| `core:tenant:update` | Modify tenant settings/billing. |
| `core:role:manage` | Create/Update custom roles. |
| `core:user:invite` | Invite new users to tenant. |
| `core:user:update` | Deactivate users / Change roles. |

### 1.2. Task Domain
| Permission String | Description |
| :--- | :--- |
| `task:project:create` | Create/Archive projects. |
| `task:project:view` | View project details. |
| `task:item:create` | Create backlog items (Stories/Bugs). |
| `task:item:edit` | Edit any backlog item (Priority/Assignee). |
| `task:item:comment` | Add comments to items. |

### 1.3. Worklog Domain
| Permission String | Description |
| :--- | :--- |
| `work:timer:start` | Start/Stop work timer. |
| `work:log:view_own` | See own history. |
| `work:log:view_team` | See time logs of others in team. |
| `work:log:view_all` | See all time logs in tenant. |

### 1.4. Monitoring Domain
| Permission String | Description |
| :--- | :--- |
| `monitor:data:view_team` | View screenshots/activity of team members. |
| `monitor:data:view_all` | View screenshots/activity of everyone. |
| `monitor:config:manage` | Change screenshot frequency / transparency rules. |

### 1.5. Report Domain
| Permission String | Description |
| :--- | :--- |
| `report:productivity:view` | View efficiency/cost reports. |
| `report:audit:view` | View security/compliance logs. |
| `report:export` | Download CSV/PDF data. |

---

## 2. System Roles Matrix

These roles are immutable system defaults.

| Feature Scope | Permission | OWNER | ADMIN | MGR | LEAD | DEV | VIEW |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tenant** | `core:tenant:update` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| | `core:role:manage` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Users** | `core:user:invite` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Projects** | `task:project:create` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| | `task:project:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Tasks** | `task:item:create` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| | `task:item:edit` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Worklogs** | `work:timer:start` | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| | `work:log:view_team` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Monitoring** | `monitor:data:view_team` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| | `monitor:data:view_all` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Reports** | `report:productivity:view` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| | `report:audit:view` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Custom Roles (Enterprise)

Enterprise tenants can compose Custom Roles by selecting specific permissions.

### 3.1. Composition Logic
A Custom Role is defined as a JSON object stored in the IAM Database.

```json
{
  "role_name": "Billing Auditor",
  "base_role": "VIEWER",
  "permissions": [
    "core:tenant:view",
    "report:productivity:view",
    "report:export"
  ],
  "is_mutable": true
}
```

### 3.2. Evaluation Rule
When evaluating permissions for a Custom Role:
1.  Start with `base_role` permissions (e.g., `VIEWER` has basic read access).
2.  **ADD** explicit permissions from the `permissions` list.
3.  **Result**: The union of Base + Explicit.

---

## 4. Special "AI Agent" Role

The `AI_AGENT` is a system service account used by the RAG Engine.

-   **Permissions**: Dynamic.
-   **Behavior**: It impersonates the calling user via **On-Behalf-Of (OBO)** flow.
-   **Effective Permission**: `Intersection(AI_AGENT_Base, Calling_User_Permissions)`.
    -   *Example*: If the AI Agent has `task:read` but the calling user is a `GUEST` (who can't read tasks), the AI **cannot** read the task.

---

**End of RBAC Definitions**
