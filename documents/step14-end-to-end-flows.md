# NeatSprint – Step 14: End-to-End Request Flows

This document visualizes the "Golden Paths" of the system, showing how components interact during critical user journeys.

---

## 1. Social Login Flow (Google)

This flow demonstrates how a user authenticates via a third-party provider and receives a session.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant App as Web App
    participant IAM as IAM Service
    participant Google as Google OAuth2
    participant DB as IAM Database

    User->>App: Click "Login with Google"
    App->>IAM: Redirect to /auth/social/google
    IAM->>Google: Redirect to OAuth Consent
    Google-->>IAM: Callback with Auth Code
    
    IAM->>Google: Exchange Code for Profile (OIDC)
    Google-->>IAM: Profile {email, sub, name}
    
    IAM->>DB: Upsert User (Check Tenant)
    DB-->>IAM: User Record (UUID)
    
    IAM->>IAM: Issue access_token & refresh_token
    IAM-->>App: Set HttpOnly Cookie / Return JSON
    App-->>User: Redirect to Dashboard
```

**Security Notes**:
-   **JIT Provisioning**: User is created on-the-fly if the email domain matches a tenant.
-   **Token scope**: Includes `tid` (Tenant ID) and `roles`.

---

## 2. Protected Action: Create Project (RBAC)

This flow shows the "Security Gauntlet" at the API Gateway before a request reaches the service.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Gateway as Traefik Gateway
    participant Auth as ForwardAuth (IAM)
    participant Svc as Task Service
    participant DB as Task DB

    Client->>Gateway: POST /tasks/projects {name: "Q2 Launch"}
    
    rect rgb(240, 240, 240)
        note right of Gateway: Security Gauntlet
        Gateway->>Gateway: Rate Limit Check
        Gateway->>Auth: Verify JWT & Permissions
        
        alt Missing Permission (TASK_CREATE)
            Auth-->>Gateway: 403 Forbidden
            Gateway-->>Client: 403 Error
        else Authorized
            Auth-->>Gateway: 200 OK (X-User-ID, X-Tenant-ID)
        end
    end
    
    Gateway->>Svc: Proxy Request
    Svc->>DB: INSERT INTO projects ...
    DB-->>Svc: New ID
    Svc-->>Gateway: 201 Created {id: "..."}
    Gateway-->>Client: 201 Created
```

---

## 3. High-Security Flow: Screenshot Upload

Demonstrates **Client-Side Encryption** to ensuring zero-knowledge privacy for the server.

```mermaid
sequenceDiagram
    autonumber
    participant Agent as Desktop Agent
    participant Svc as Monitor Service
    participant S3 as Object Storage (S3)
    participant DB as Monitor DB

    Agent->>Agent: Capture Screenshot
    Agent->>Agent: Encrypt (AES-256-GCM) with Tenant Key
    
    Agent->>Svc: POST /monitor/screenshots (Metadata + Blob)
    
    Svc->>Svc: Validate Session & Quota
    
    par Parallel Storage
        Svc->>S3: PutObject (Encrypted Blob)
        Svc->>DB: Insert Metadata (path, captured_at)
    end
    
    Svc-->>Agent: 202 Accepted
```

**Privacy Guarantee**: The server *never* sees the unencrypted image.

---

## 4. Privacy Feature: "Delete Screenshot"

Shows how we handle "Right to Erasure" while maintaining auditability.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Svc as Monitor Service
    participant DB as Monitor DB
    participant S3 as Object Storage

    User->>Svc: DELETE /monitor/screenshots/{id}
    
    Svc->>Svc: Check "Deletion Window" (e.g., < 24h old)
    
    alt Window Expired
        Svc-->>User: 403 Deletion Window Closed
    else Allowed
        Svc->>S3: DeleteObject (Blob)
        Svc->>DB: UPDATE screenshots SET deleted=true, path=NULL
        Svc-->>User: 204 No Content
    end
```

**Result**:
-   **Manager Report**: Shows "Deleted by User" placeholder.
-   **AI Training**: Skipped (Content is gone).

---

**End of Request Flows**
