# NeatSprint – Step 9: Authorization Enforcement Flow (RBAC)

This document details the runtime security model, explaining how permissions are issued, cached, and enforced across the microservices architecture.

---

## 1. Principles
-   **Zero Trust**: Internal services must still validate JWTs (unless mTLS is strictly enforced, but token passing is preferred for context).
-   **Policy Decoupling**: Authorization logic (Policies) is separate from Business Logic.
-   **Fail-Closed**: If the IAM service or Cache is down, access is DENIED.

---

## 2. RBAC Logic Model

Authorization is an intersection of **Who** (Identity) and **What** (Resource).

### 2.1. The "Intersection" Rule
Access is **ALLOWED** if and only if:
1.  The User has a **Role** in the target **Tenant**.
2.  That **Role** contains a **Permission**.
3.  That **Permission** matches the **Required Capability** of the content being accessed.

```mermaid
graph LR
    subgraph Identity
    User -- Assigned --> Role
    Role -- Includes --> Permission
    end
    
    subgraph Request
    API_Call -- Requires --> Capability
    end
    
    Permission -. Matches .-> Capability
    
    style Capability fill:#f9f,stroke:#333
    style Permission fill:#bbf,stroke:#333
```

---

## 3. Login & Token Issuance Flow

This flow describes how a user obtains a **JWT Access Token** containing the necessary claims.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant App as Client App
    participant IAM as IAM Service
    participant DB as IAM Database

    User->>App: Click Login (Credentials/SSO)
    App->>IAM: POST /auth/login
    IAM->>DB: Verify Credentials
    DB-->>IAM: OK (User ID, Tenant ID)
    
    par Parallel Fetch
        IAM->>DB: Fetch Active Roles
        IAM->>DB: Fetch Feature Flags
    end
    
    IAM->>IAM: Construct JWT Claims
    note right of IAM: Claims: { uid, tid, roles: ["admin"], scopes: [...] }
    
    IAM->>IAM: Sign Token (RS256 Private Key)
    IAM-->>App: Return { AccessToken, RefreshToken }
    App->>App: Secure Storage (HttpOnly Cookie / Keychain)
```

---

## 4. Runtime Enforcement Flow

This flow explains how a request is validated at the **API Gateway** level before reaching microservices. This "Fast Path" uses Redis to avoid database bottlenecks.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant GW as API Gateway
    participant Redis as Redis Cache
    participant Service as Target Microservice

    Client->>GW: GET /api/v1/projects (Auth Header: Bearer JWT)
    
    GW->>GW: 1. Validate JWT Signature (Public Key)
    GW->>GW: 2. Check Expiration (exp)
    
    alt Signature Invalid / Expired
        GW-->>Client: 401 Unauthorized
    else Token Valid
        GW->>Redis: 3. Check Revocation Blacklist (jti)
        
        alt Token Revoked
            Redis-->>GW: Yes
            GW-->>Client: 401 Unauthorized
        else Token Active
            GW->>GW: 4. Extract Roles from Claims
            GW->>Redis: 5. Get Permissions for Role: "Manager"
            Redis-->>GW: Returns [PROJECT.VIEW, PROJECT.EDIT...]
            
            GW->>GW: 6. Match Route Requirement (PROJECT.VIEW)
            
            alt Permission Granted
                GW->>Service: Proxy Request (Injected Headers: X-User-ID, X-Tenant-ID)
                Service-->>Client: 200 OK (Data)
            else Permission Denied
                GW-->>Client: 403 Forbidden
            end
        end
    end
```

---

## 5. Caching & Performance Strategy

To ensure low latency (< 20ms overhead), we rely heavily on **Redis**.

### 5.1. Cached Entities
| Key Pattern | Value | TTL | Description |
| :--- | :--- | :--- | :--- |
| `rbac:role:{role_id}` | List of Permission Strings | 1 Hour | Maps Role UUID to `["App.Feat.Action", ...]` |
| `auth:revoked:{jti}` | Timestamp | Exp of Token | **Blacklist**. If present, token is rejected. |
| `tenant:config:{id}` | JSON Config | 15 Mins | Tenant status, plan limits. |

### 5.2. Cache Invalidation
-   **Event**: Admin updates a Role (adds permission).
-   **Action**: IAM Service publishes `event.rbac.update` to Pub/Sub.
-   **Subscriber**: API Gateway clears `rbac:role:{role_id}` from Redis.
-   **Result**: Next request causes a cache miss -> fetch from DB -> Write to Redis.

---

**End of Authorization Flow**
