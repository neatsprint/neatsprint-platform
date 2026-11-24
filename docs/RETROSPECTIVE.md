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
- [ ] Close M5 open items: virus scanning, shared lockout, SBOM gate, UAT, legal review, v1.0.0.
