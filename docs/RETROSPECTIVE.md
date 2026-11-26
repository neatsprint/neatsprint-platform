# M0–M5 Retrospective (pre-P2)

Date: 2026-11-24 · Author: OpenCade · Owner review: Laksiri

## What worked

- Vertical slices per milestone: schema → API → tests → web → docs kept the system runnable.
- Outbox + Redis Streams made cross-service features (access cache, notifications, reports)
  possible without shared databases.
- Shared `neatsprint-lib` avoided re-implementing auth, errors, DB and metrics.
- Live end-to-end verification caught real issues (privacy window promotion, team scope caching,
  event payload gaps).
- Explicit ADRs prevented accidental stack drift (Tauri retained, desktop deferred).

## What to change

1. **Toolchain preflight** — verify Rust/Tauri, signing certificates and capture lab before
   committing to desktop milestones; the M3 desktop block stalled on missing tooling.
2. **Contract-first events** — item/time/screenshot event payloads needed enrichment after the
   projectors were written. Define event schemas in `neatsprint-contracts` before producers.
3. **Backfill from day one** — add source-internal paginated endpoints with the first service, not
   during hardening.
4. **Seed realism** — keep a richer demo dataset (multi-sprint, time, captures) in a fixture so
   reports and galleries are testable after every reset.
5. **Accessibility in the definition of done** — add axe checks per screen, not only at M5.
6. **Ops early** — resource limits, alerts and runbooks should land with the first deployable
   stack, not only at hardening.
7. **Branch protection** — the IAM ruleset initially required a non-existent check; codify
   rulesets in the repo and verify them in CI.

## P2 kickoff checklist

- [ ] Finalize chat schema and channel/team binding ADR.
- [ ] Add event contracts for chat, presence and notifications.
- [ ] Extract the notification service and add push token registry.
- [ ] Scaffold Expo mobile with auth, assigned work and offline queue.
- [ ] Add GitHub commit/PR linking with least-privilege installation tokens.
- [ ] Carry desktop T22–T36 into P2 planning with a Rust/Tauri toolchain owner.
- [ ] Close remaining M5/post-v1.0.2 items: 72-hour health window (`M5-T26`), external legal counsel review, and the post-v1.0.2 required improvements in `DEVELOPMENT_PLAN.md` §8.1.

## Required Improvements Identified After v1.0.2

1. **Streaming SSR vs route `loading.tsx` skeletons** — Next.js 16 production standalone builds left
   route-level `loading.tsx` boundaries stuck on `"Loading…"` in the browser even though the server
   streamed complete HTML (`v1.0.2` removed `loading.tsx` to fix rendering). Investigate Next.js 16
   RSC streaming / reverse-proxy buffering before re-introducing suspense skeletons.
2. **UI CRUD completeness checks at milestone gates** — `v1.0.0` passed API and UAT checks while
   missing web UI controls for creating backlog items (fixed in `v1.0.1`) and adding/removing team
   members (fixed in `v1.0.2`), and with the `Reports` desktop sidebar link disabled. Gate reviews
   must verify every create/edit/delete user journey through the rendered browser UI, not only via
   API tests.
3. **Container volume mount verification** — `bitnamilegacy/minio` writes to `/bitnami/minio/data`,
   so the initial `/data` mount left objects ephemeral until fixed during UAT. Always verify data
   persistence across container recreation (`--force-recreate`) when adding stateful containers.
4. **Database-enforced tenant isolation across all services** — PostgreSQL RLS was added to Task and
   Team in M2, but Reports, Worklog, Monitoring and IAM still rely on application-level
   `tenant_id` filters (which allowed an unscoped `session.get(ReportSprintFact, sprint_id)` in
   `neatsprint-reports`). Extend RLS across all tenant-owned tables.
