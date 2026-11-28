# NeatSprint — Architecture Decision Records (ADRs)

> **Status**: Living document · **Last updated**: 2026-11-21
> **Owner**: Laksiri Fernando (approver) · **Author**: OpenCade (AI)
> **Rule**: Any decision that changes architecture, vendor, cost, licensing or scope is recorded
> here **before** implementation. "Proposed" means the default is assumed until Laksiri objects.

Status values: `Proposed` · `Accepted` · `Rejected` · `Superseded by ADR-xxx`.

---

## ADR-001 — Backend services use Python 3.12 + FastAPI

- **Status**: Accepted
- **Context**: The reference set is contradictory: Step 1 says "Node.js/Go/Rust", while
  `tech-design.md` and its standard layout specify FastAPI with `pyproject.toml`. We need one
  language for nine services, sharing libraries for auth, DB, events and errors.
- **Decision**: All backend services use Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 async,
  Alembic, Ruff, mypy, pytest and `uv` for dependency resolution.
- **Rationale**: Strongest alignment with the existing design documents; best ecosystem for the
  later AI service; fastest path for one small team; generated TS clients remove the need for a
  shared language with the frontend.
- **Consequences**: Two languages (Python + TypeScript) in the codebase; performance is adequate
  for the stated scale; heavy AI/CPU work can be isolated in workers.
- **Alternatives considered**: NestJS/TypeScript (single language, weaker AI ecosystem, more
  boilerplate); Go (fast, but slower iteration and weaker AI ergonomics); **Next.js as the backend
  (rejected — see ADR-018; it is a UI framework, not a service runtime)**.
- **Clarification (2026-11-21)**: the comparison is Python vs Node/TypeScript for services, not
  FastAPI vs Next.js. Next.js remains the web UI and BFF only.
- **Revisit if**: p95 targets cannot be met after profiling, or the team grows a strong TS backend
  preference.

---

## ADR-002 — Database per service on one cluster for MVP

- **Status**: Accepted
- **Context**: Microservice isolation requires owned data. Separate physical clusters multiply cost
  and operational burden for a small team.
- **Decision**: Each service owns a **logical database** (`db_iam`, `db_task`, …) on a single
  PostgreSQL 16 cluster in MVP. Credentials are per service, cross-database access is forbidden,
  and migrations are per service. Move to separate clusters when scale or compliance requires.
- **Consequences**: Cost-efficient; isolation enforced by credentials and code review plus tests;
  a noisy neighbour can affect all services (mitigated by limits and monitoring).
- **Alternatives**: Schema-per-service in one DB (weaker boundary); separate clusters (expensive).

---

## ADR-003 — API gateway is Traefik v3

- **Status**: Accepted
- **Context**: Need routing, TLS, rate limiting, ForwardAuth, headers and observability with minimal
  configuration in Compose and Kubernetes.
- **Decision**: Traefik v3 with ForwardAuth to IAM, Redis-backed rate limiting, security-header
  middleware, and OpenTelemetry tracing.
- **Consequences**: Auto-discovery in Compose; configuration is declarative; plugin ecosystem is
  smaller than Kong's, which we do not need.
- **Alternatives**: Kong (heavier, stronger plugin ecosystem), Nginx (manual config), Envoy (steep).

---

## ADR-004 — UUIDv7 for all identifiers, client-generated where offline

- **Status**: Accepted
- **Context**: Desktop and mobile must create records offline; sequential IDs leak volume and are
  unusable offline.
- **Decision**: UUIDv7 primary keys everywhere. Offline-capable entities (time entries, screenshots,
  comments) are generated on the client and used as idempotency keys.
- **Consequences**: Time-sortable indexes, no central sequence, larger keys (16 bytes); clients must
  have a correct UUIDv7 implementation (provided in `neatsprint-lib` and the TS SDK).
- **Alternatives**: UUIDv4 (no sort order), ULID (similar but less standard support), bigint
  sequences (offline-hostile).

---

## ADR-005 — Screenshots use KMS envelope encryption, not end-to-end encryption

- **Status**: Accepted
- **Context**: The reference documents claim both "the server never sees the image" and "AI analyses
  screenshots" / "managers view screenshots". These are mutually exclusive.
- **Decision**: Screenshots are encrypted at rest with per-object data keys wrapped by a tenant KMS
  key (AES-256-GCM). The server can decrypt only for an authorised request, and every decryption is
  audited. Local capture is encrypted on the device before upload.
- **Rationale**: Manager review and AI summaries are core product requirements. True E2E would make
  them impossible without client-side key sharing, which contradicts browser-based manager review.
- **Consequences**: Marketing must not claim end-to-end encryption; privacy relies on access control,
  audit, deletion and key destruction. Deleting an object also destroys its wrapped key
  (crypto-shredding).
- **Alternatives**: True E2E (drops manager gallery and AI); no encryption at rest (unacceptable).

---

## ADR-006 — The privacy window is server-authoritative with a pending state

- **Status**: Accepted
- **Context**: The reference design describes the deletion window both as a local-only grace period
  (Step 8) and as a server-side API check (Step 14). Two sources of truth would allow bypasses.
- **Decision**: Uploaded screenshots enter `PENDING` (owner-only). The server owns `visible_after`.
  Deletion is allowed only while pending and destroys the blob, the wrapped key, and any derived
  embeddings. At window end the row becomes `VISIBLE`. Managers can never fetch pending content.
  Blobs are excluded from backups.
- **Consequences**: A device that stays offline past the window may still show local pending items;
  the agent must reconcile state on reconnect. Backups cannot restore a deleted screenshot, by
  design.
- **Alternatives**: Client-only window (bypassable by clock/agent tampering); immediate visibility
  (removes the trust feature).

---

## ADR-007 — Defence in depth: services validate JWTs as well as the gateway

- **Status**: Accepted
- **Context**: Step 4 says services trust injected headers; Step 9 says zero trust. Header trust
  makes a gateway bypass catastrophic.
- **Decision**: The gateway validates and injects identity, **and** each service validates the JWT
  signature/claims against JWKS, re-checks tenant and permission, and strips untrusted identity
  headers. Internal calls use short-lived service tokens.
- **Consequences**: Small per-request cost (cached JWKS, parsed claims); a compromised gateway alone
  cannot impersonate users; tests must cover both layers.
- **Alternatives**: Gateway-only (faster, fragile); mTLS-only (does not carry user identity).

---

## ADR-008 — Reports use read-model projections, not cross-database joins

- **Status**: Accepted
- **Context**: Step 19 proposes querying read replicas of several service databases. PostgreSQL
  cannot join across databases, and direct replica access violates service ownership.
- **Decision**: The reports service maintains its own projection tables fed by domain events
  (outbox → Redis Streams). Projections are idempotent, replayable and rebuildable. A backfill job
  seeds history from source APIs.
- **Consequences**: Eventual consistency (seconds), extra storage, projector code to maintain; in
  exchange, report queries never touch operational databases and can be optimised independently.
- **Alternatives**: Cross-DB foreign data wrappers (fragile), shared reporting schema (coupling),
  data warehouse at MVP (premature).

---

## ADR-009 — Events use transactional outbox + Redis Streams in MVP

- **Status**: Accepted
- **Context**: Services must notify each other reliably without a heavyweight broker in MVP.
- **Decision**: Domain events are written to an outbox table in the same transaction as the state
  change, then published to Redis Streams with consumer groups and idempotency keys. Dead-letter
  stream for poison messages.
- **Consequences**: At-least-once delivery; consumers must be idempotent; Redis becomes
  infrastructure-critical (outbox buffers outages). Kafka can replace the transport later without
  changing producers.
- **Alternatives**: Kafka from day one (operational overhead), direct HTTP calls (fragile, coupling),
  DB triggers (hidden behaviour).

---

## ADR-010 — Desktop device binding uses a key pair, not hardware fingerprints

- **Status**: Accepted
- **Context**: Step 16 proposes CPU serial, disk UUID and MAC address. These are spoofable, change
  on hardware upgrades, and are privacy-invasive to collect.
- **Decision**: The agent generates an Ed25519 key pair, registers the public key, keeps the private
  key in the OS keychain (TPM/Secure Enclave when available), and signs a per-request proof over
  method, path, body hash, nonce and timestamp. Revocation is server-side.
- **Consequences**: Stronger and less invasive; requires clock-skew tolerance and replay protection;
  a copied token is useless without the private key.
- **Alternatives**: Hardware fingerprint hash (brittle, spoofable), mTLS client certificates
  (heavier operations for a desktop fleet).

---

## ADR-011 — Chat and mobile are Phase 2; MVP excludes them

- **Status**: Accepted
- **Context**: The MVP must prove trust (tracking + privacy) and planning before adding surface area.
- **Decision**: MVP ships web + desktop + 9 backend services. Chat, notifications, mobile and
  GitHub integration are Phase 2. Contracts and IDs are designed to accept them later.
- **Consequences**: Faster MVP, lower risk; competitive gap on mobile until P2.
- **Alternatives**: Include chat (scope creep, WebSocket complexity), include mobile (doubles client
  QA).

---

## ADR-012 — Tenants have many users; each account belongs to one tenant

- **Status**: Accepted (clarified 2026-11-21)
- **Context**: "One user, one tenant" was ambiguous. The intended model is **one tenant → many
  users**, each logging in and working independently. The restriction is the inverse: a user
  account is a member of exactly one tenant. Consultants and agencies, however, often need one
  person in several workspaces.
- **Decision**:
  1. A tenant has many users (seats limited by plan).
  2. A user account has exactly one `tenant_id`; tokens carry a single `tid`.
  3. **Email addresses are globally unique** across the platform (`UNIQUE(email)`), so login and
     Google/OIDC linking are unambiguous. The same email cannot be invited into a second tenant.
  4. A person needing two workspaces uses two accounts with distinct emails in MVP.
  5. Inviting an email that already belongs to another tenant returns a neutral `409
     email_unavailable`; it must never reveal the other tenant's name or existence.
  6. Single-login multi-tenant access (identity + memberships + workspace selector) is a later
     feature requiring its own ADR and migration.
- **Consequences**: Simple login (`email + password`), simple tokens, simple scoping; a documented
  limitation for consultants; support process needed for account/tenant moves. Global email
  uniqueness slightly reduces signup flexibility but removes a whole class of ambiguity.
- **Alternatives**: Per-tenant email uniqueness with a workspace selector at login (better for
  consultants, more auth complexity and enumeration surface); subdomain-per-tenant (clean but adds
  TLS/routing/cookie complexity); full identity + many memberships (correct long-term model, larger
  MVP).

---

## ADR-013 — Multi-repo with git submodules and a contracts repository

- **Status**: Accepted
- **Context**: The brief requires separate repositories per service/client, while a small team needs
  a single integration point.
- **Decision**: 15 component repositories plus this orchestrator; `neatsprint-contracts` is the
  single source of API/event schemas; `neatsprint-lib` holds shared Python code; the orchestrator
  pins submodule commits and deploys from a platform tag.
- **Consequences**: Independent releases and clear ownership; more CI setup and version juggling.
  Mitigated by templates and contract generation.
- **Alternatives**: Monorepo (simpler CI, contradicts the brief), few large repos (loses independent
  release cadence).

---

## ADR-014 — Web stack is Next.js 15 + Tailwind + shadcn/ui

- **Status**: Accepted
- **Context**: Need a fast, accessible, maintainable management console with server rendering for
  first paint and an auth BFF for httpOnly cookies.
- **Decision**: Next.js App Router, TypeScript strict, Tailwind CSS, shadcn/ui primitives, TanStack
  Query for server state, Zustand for UI state, Recharts for charts.
- **Consequences**: Strong ecosystem and hiring pool; App Router complexity must be managed with
  conventions; server components keep tokens off the client.
- **Alternatives**: Vite SPA (simpler, weaker auth story), Remix (viable), plain React (more glue).

---

## ADR-015 — Billing is manual in MVP; Stripe arrives in Phase 3

- **Status**: Accepted
- **Context**: Plans and limits are in scope; payment processing is not part of the trust story.
- **Decision**: The platform operator assigns a plan to a tenant via an operator endpoint/script.
  Plan limits are enforced. Stripe (subscriptions, seats, invoices, webhooks) is Phase 3.
- **Consequences**: No self-serve checkout at launch; finance handled manually for early customers.
- **Alternatives**: Stripe at MVP (adds PCI scope, webhooks, dunning, and weeks of work).

---

## ADR-016 — Screenshot blobs are excluded from backups

- **Status**: Accepted
- **Context**: If deleted screenshots could be restored from a backup, the privacy promise would be
  false.
- **Decision**: Object storage backups/cross-region replication exclude the screenshot bucket.
  Only metadata (including tombstones) is backed up with the database.
- **Consequences**: A storage failure loses active screenshots (acceptable: they are transient
  evidence, retention-bounded). Restore cannot resurrect deleted images.
- **Alternatives**: Back up blobs with short retention (risk of resurrection), legal-hold exception
  (P3, explicit and disclosed).

---

## ADR-017 — Monotonic client clocks plus server clamp for durations

- **Status**: Accepted
- **Context**: Desktop time tracking is vulnerable to system clock changes and sleep/hibernate.
- **Decision**: Measure elapsed time with a monotonic clock; send elapsed seconds with each sync;
  the server clamps against wall-clock time, flags discrepancies beyond a threshold, and stores the
  skew in the session.
- **Consequences**: Clock rollback cannot inflate time; legitimate long offline sessions still work;
  anomalies are visible to admins instead of silently trusted.
- **Alternatives**: Trust client timestamps (fraud-prone), server-only timing (breaks offline).

---

## ADR-018 — Runtime language policy: Python services, Rust for CPU-bound components, TypeScript clients

- **Status**: Accepted
- **Context**: Question raised by Laksiri (2026-11-21): "why FastAPI over Next.js?" and "how about
  Rust for CPU-intensive work?" The platform is inherently polyglot (Next.js web, Tauri/Rust
  desktop), so the real question is where each runtime earns its place.
- **Decision**:
  1. **Domain services** remain Python 3.12 + FastAPI (ADR-001).
  2. **Next.js is never a service runtime.** It is the web UI plus a thin BFF for httpOnly cookie
     sessions. Using it as a backend would mean 9 React-bundled deployments with no long-lived
     consumers, no durable queue workers, weak WebSocket support for P2 chat, and serverless-shaped
     timeouts — the wrong shape for this architecture.
  3. **Rust is the default for CPU-bound, memory-constrained, or endpoint-resident components.**
     Already true for the desktop agent (capture, image encode, AES-GCM, hashing, SQLCipher, idle
     detection). It becomes the choice for a new component only when profiling proves CPU-bound
     work that cannot be solved by a library or configuration.
  4. **Exhaust the boring option first**: `libvips`/`pyvips`, OpenCV, Pillow, `orjson`, PostgreSQL
     aggregation, and worker parallelism before adding Rust. A Rust rewrite of a DB-bound CRUD
     service is prohibited by this policy.
  5. **Rust integration shape**: a narrow-interface worker/CLI (or a PyO3 extension when the call
     overhead dominates), with a versioned contract, deployed beside the service. Never a
     big-bang rewrite.
  6. **TypeScript backend (NestJS/Fastify)** remains a legitimate alternative but requires a new
     ADR with a team-capability rationale; it is not selected for MVP.
- **Rationale**: Python maximises delivery speed for I/O-bound orchestration (auth, CRUD,
  validation, reporting SQL) and keeps the AI/analytics headroom. Rust is genuinely superior where
  cycles and memory matter (desktop, media, crypto) and is already required for Tauri, so it is a
  targeted tool rather than a second backend platform. Contract-first OpenAPI generation preserves
  end-to-end TypeScript types for clients, so a Python backend does not cost the frontend its type
  safety.
- **Consequences**: Two backend languages on the server side (Python, plus Rust only in isolated
  components); a benchmark gate at M3 decides whether the media pipeline needs Rust; CI must build
  Rust artefacts only for the desktop and any approved worker.
- **Benchmark gate (M3)**: encrypt + thumbnail + hash of a 1 MB capture should complete in
  < 50 ms and the agent should stay < 2% average CPU / < 250 MB RSS. If Python/libvips misses this
  on the capture path, the media pipeline moves to Rust.
- **Alternatives**: All-Rust backend (Axum + sqlx): excellent runtime, slower CRUD/iteration and
  thinner LLM/reporting ecosystem; all-TypeScript backend: fewest languages, but poor fit for
  background consumers and AI data work; Next.js backend: rejected outright.

---

## ADR-019 - Desktop agent stays Tauri v2 + Rust; desktop build deferred

- **Status**: Accepted
- **Date**: 2026-11-24
- **Context**: Laksiri asked whether .NET or another stack would be better for the desktop
  agent. The machine has .NET 10 but no Rust/Tauri toolchain. The agent is tray-first and needs
  native capture, idle detection, OS keychain, SQLCipher, signed updates and low memory.
- **Decision**: Keep **Tauri v2 + Rust + React/TypeScript** as planned. Do not switch to .NET,
  Avalonia, Electron, Flutter or Qt. Park `M3-T22..T36` until a Rust/Tauri toolchain and Windows
  capture lab are available; continue with the rest of the MVP (M4 and M5) in the meantime.
- **Why**: No desktop code exists yet, so either stack was viable, but switching buys little:
  both Tauri and Avalonia still require per-OS capture/idle/keychain code; Tauri keeps the
  smallest footprint, the strongest sandbox/security story, and reuses TypeScript UI skills. .NET
  would be faster on Windows-only capture, but adds a third runtime and a later cross-platform
  rewrite or Avalonia dependency.
- **Consequences**: M3 remains 25/40; the M3 exit gate (4-hour offline run and desktop deletion
  evidence) is carried forward. Notification/monitoring web screens and backend privacy work are
  already delivered. Revisit only if the Windows capture spike with Tauri fails its CPU/RSS gate.
- **Alternatives**: .NET 10 + Avalonia (strong Windows capture and packaging, but stack change and
  larger footprint); .NET MAUI/WinUI (Windows lock-in); Electron (memory/attack surface).

---

## ADR-020 - Desktop agent development resumed on a Windows toolchain

- **Status**: Accepted
- **Date**: 2026-11-28
- **Context**: ADR-019 parked `M3-T22..T36` until a Rust/Tauri toolchain and a Windows capture lab
  were available. Laksiri has decided to start desktop development now. The workstation is Windows
  11 Pro (12 cores, 88 GB free) with WebView2 158, Node 24 via nvm4w, Git and winget, but no Rust,
  no MSVC C++ tools and no Windows SDK.
- **Decision**: Resume the desktop agent as **Tauri v2 + Rust + React/TypeScript**, Windows first,
  and lift the deferral in ADR-019. Baseline toolchain: Rust stable `x86_64-pc-windows-msvc`,
  Visual Studio 2022 Build Tools with the C++ workload and Windows 11 SDK, **Node 22 LTS** for
  parity with web/CI, and NASM + Strawberry Perl so SQLCipher can build against vendored OpenSSL.
  Setup steps live in `docs/DESKTOP_AGENT_SETUP.md`; `scripts/check-desktop-prereqs.ps1` verifies a
  machine.
- **Consequences**: `M3-T22..T36` are actionable again and the M3 exit gate (4-hour offline run,
  desktop deletion evidence) is still open until they land. The desktop repo gains a Windows CI
  workflow. macOS builds stay deferred (unsigned dev build at `M3-T34` only). No change to the stack
  choice itself; ADR-019's rationale stands.
- **Alternatives**: stay on the deferred path until M6; switch to .NET/Avalonia (rejected again for
  the same reasons as ADR-019).

---

## Decision Log Summary

| ADR | Title | Status | Milestone |
| :--- | :--- | :--- | :--- |
| 001 | Python + FastAPI | Accepted | M0 |
| 002 | DB per service on one cluster | Accepted | M0 |
| 003 | Traefik gateway | Accepted | M0 |
| 004 | UUIDv7 identifiers | Accepted | M0 |
| 005 | KMS envelope encryption for screenshots | Accepted | M3 |
| 006 | Server-authoritative privacy window | Accepted | M3 |
| 007 | Defence-in-depth JWT validation | Accepted | M1 |
| 008 | Reporting projections | Accepted | M4 |
| 009 | Outbox + Redis Streams | Accepted | M0 |
| 010 | Device key-pair binding | Accepted | M3 |
| 011 | Chat/mobile in Phase 2 | Accepted | — |
| 012 | Many users per tenant; account belongs to one tenant (global unique email) | Accepted | M1 |
| 013 | Multi-repo + contracts | Accepted | M0 |
| 014 | Next.js web stack | Accepted | M0 |
| 015 | Manual billing in MVP | Accepted | M1 |
| 016 | No screenshot backups | Accepted | M3 |
| 017 | Monotonic time + server clamp | Accepted | M3 |
| 018 | Runtime language policy (Python / Rust / TS) | Accepted | M3 |
| 019 | Desktop agent stays Tauri v2 + Rust; deferred | Accepted | M3/M4 |
| 020 | Desktop agent development resumed on a Windows toolchain | Accepted | M3 |

## Change Log

| Date | Change |
| :--- | :--- |
| 2026-11-21 | ADR-001…017 recorded during initial planning |
| 2026-11-21 | ADR-018 added: runtime language policy (Python services, Rust for CPU-bound work, Next.js not a backend) |
| 2026-11-24 | ADR-019 added: keep Tauri v2 + Rust for the desktop agent; defer M3 desktop tasks |
| 2026-11-28 | ADR-020 added: desktop agent development resumed on the Windows Rust/Tauri toolchain |

---

## Required Improvements (Post-v1.0.2 Review)

- [ ] **IMP-ADR-01 (Update ADR-014 for Next.js 16 & npm)**: Record an amendment to ADR-014 noting
  the M5 upgrade from Next.js 15 to **Next.js 16.4.6** (Vitest 5 / Vite 7) to clear high/critical
  dependency advisories, the use of `npm` (`package-lock.json`), and the removal of route-level
  `loading.tsx` files in `v1.0.2` to work around Next.js 16 standalone RSC streaming behavior.
- [ ] **IMP-ADR-02 (Record PDF rendering decision from M4)**: Add a brief note or ADR recording the
  selection of **ReportLab** over headless Chromium/WeasyPrint for M4 PDF exports (`ARCHITECTURE.md`
  §17, `RELEASE_NOTES.md`).
