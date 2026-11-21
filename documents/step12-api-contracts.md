# NeatSprint – Step 12: API Contracts

This document defines the interface for the NeatSprint Platform.

## Global Standards

*   **Base URL**: `https://api.neatsprint.com/api/v1`
*   **Content-Type**: `application/json`
*   **Date Format**: ISO 8601 UTC (e.g., `2024-03-20T14:30:00Z`)
*   **ID Format**: **UUIDv7** (Time-ordered 128-bit UUIDs)

## Interactive Documentation
The live API documentation (OpenAPI / Swagger UI) is available at:
*   **Production**: `https://api.neatsprint.com/docs`
*   **Staging**: `https://staging-api.neatsprint.com/docs`
*   **Local**: `http://localhost:8000/docs`

### Common Headers
All protected endpoints require:
```http
Authorization: Bearer <access_token>
X-Tenant-ID: <tenant_uuid>
```

### Standard Response Envelope (Success)
```json
{
  "data": { ... },
  "meta": { "page": 1, "limit": 50, "total": 120 } // Optional pagination
}
```

---

## 1. IAM Service (`neatsprint-iam`)

### 1.1. Login (Email/Password)
**POST** `/auth/login`

**Request**
```json
{
  "email": "jane.doe@example.com",
  "password": "secure_password_123",
  "device_id": "018e6b18-8f83-7c39-8264-123456789012" // Required for Device Binding
}
```

**Response (200 OK)**
```json
{
  "access_token": "eyJhbGciOiJSUzI1Ni...",
  "refresh_token": "eyJhbGciOiJSUzI1Ni...",
  "expires_in": 900,
  "token_type": "Bearer",
  "user": {
    "id": "018e6b1b-9f12-7445-9a21-abcdefabcdef",
    "email": "jane.doe@example.com",
    "full_name": "Jane Doe",
    "role_codes": ["TENANT_ADMIN", "TASK_MANAGER"]
  }
}
```

### 1.2. Users CRUD
**POST** `/users`
*Requirement: `TENANT_ADMIN` role*

**Request**
```json
{
  "email": "dev.lead@example.com",
  "full_name": "John Developer",
  "role_ids": ["018e6b1c-XXXX-XXXX-XXXX-XXXXXXXXXXXX"]
}
```

**Response (201 Created)**
```json
{
  "id": "018e6b20-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "email": "dev.lead@example.com",
  "status": "ACTIVE",
  "created_at": "2024-03-20T10:00:00Z",
  "updated_at": "2024-03-20T10:00:00Z",
  "created_by": "018e6b1b-9f12-7445-9a21-abcdefabcdef"
}
```

---

## 2. Core Platform (`neatsprint-core`)

### 2.1. Tenant Applications
**GET** `/tenant-applications`
*Returns enabled modules for the current tenant.*

**Response (200 OK)**
```json
[
  {
    "application_code": "TASK_MGMT",
    "enabled": true,
    "enabled_at": "2024-01-01T00:00:00Z"
  },
  {
    "application_code": "AI_ASSISTANT",
    "enabled": false
  }
]
```

---

## 3. Team Management (`neatsprint-team`)

### 3.1. List Teams
**GET** `/teams`

**Response (200 OK)**
```json
[
  {
    "id": "018e6b30-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "name": "Backend Squad",
    "member_count": 5,
    "created_at": "2024-02-15T08:00:00Z"
  }
]
```

---

## 4. Task Service (`neatsprint-task`)

### 4.1. Create Project
**POST** `/projects`

**Request**
```json
{
  "name": "Q2 Feature Launch",
  "description": "Main release for Q2",
  "start_date": "2024-04-01",
  "end_date": "2024-06-30"
}
```

### 4.2. Create Backlog Item (Task/Bug)
**POST** `/projects/{project_id}/backlog`

**Request**
```json
{
  "type": "TASK",
  "title": "Implement Login Flow",
  "priority": "HIGH",
  "assignee_user_id": "018e6b20-XXXX-XXXX-XXXX-XXXXXXXXXXXX" // ONE assignee only
}
```

**Response (201 Created)**
```json
{
  "id": "018e6b40-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "project_id": "018e6b35-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "status": "TODO",
  "created_at": "2024-03-21T09:00:00Z",
  "created_by": "018e6b1b-9f12-7445-9a21-abcdefabcdef"
}
```

---

## 5. Worklog Service (`neatsprint-worklog`)

### 5.1. Start Timer
**POST** `/work/start`

**Request**
```json
{
  "backlog_item_id": "018e6b40-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "comment": "Starting initial research"
}
```

### 5.2. Stop Timer
**POST** `/work/stop`

**Response (200 OK)**
```json
{
  "work_session_id": "018e6b50-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "duration_seconds": 3600,
  "ended_at": "2024-03-21T10:00:00Z"
}
```

---

## 6. Monitoring Service (`neatsprint-monitoring`)

### 6.1. Upload Screenshot (Encrypted)
**POST** `/monitor/upload`
*Client Must Encrypt before uploading*

**Request (Multipart/Form-Data)**
*   `file`: (Binary Blob, AES-256 Encrypted)
*   `metadata`: JSON
    ```json
    {
      "session_id": "018e6b50-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
      "captured_at": "2024-03-21T09:30:00Z"
    }
    ```

### 6.2. Delete Screenshot (Privacy)
**DELETE** `/monitor/screenshots/{screenshot_id}`
*Valid only within the "Privacy Window" (e.g., 24h)*

**Response (204 No Content)**

---

## 7. Reports Service (`neatsprint-reports`)

### 7.1. Productivity Report
**GET** `/reports/productivity?team_id=...&start_date=2024-03-01&end_date=2024-03-31`

---

## 8. AI Service (`neatsprint-ai`)

### 8.1. Generate Summary
**POST** `/ai/summary`

**Request**
```json
{
  "session_id": "018e6b50-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "context": "developer_worklog"
}
```

**Response (200 OK)**
```json
{
  "summary": "Refactored the authentication middleware to support device binding."
}
```

---

## 9. Error Handling (RFC 7807)

All errors return a standard Problem Details JSON.

**Example: 403 Forbidden**
```json
{
  "type": "https://neatsprint.com/errors/permission-denied",
  "title": "Permission Denied",
  "status": 403,
  "detail": "User does not have TASK_CREATE permission for this project.",
  "instance": "/projects/123/backlog"
}
```

| Status Code | Usage |
| :--- | :--- |
| **400** | Bad Request (Validation failed) |
| **401** | Unauthorized (Missing/Invalid Token) |
| **403** | Forbidden (RBAC violation) |
| **404** | Resource Not Found |
| **409** | Conflict (UUID collision or Unique constraint) |
| **422** | Unprocessable Entity (Logical validation) |
| **429** | Too Many Requests (Rate limit hit) |
| **500** | Internal Server Error |
