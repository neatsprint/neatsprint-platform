# Chaos-lite Test

Date: 2026-11-24 · Environment: local Docker Compose

## Scenario

1. Stop the Team service while the gateway and IAM remain healthy.
2. Call `GET /api/v1/teams` through the gateway with a valid owner token.
3. Restart Team and repeat.

## Result

| Step | Observed |
| :--- | :--- |
| Team stopped | Gateway returned `502 Bad Gateway` |
| Body | Plain text `Bad Gateway` (Traefik default) |
| Recovery | After restart and health, `GET /api/v1/teams` returned `200` |

## Findings

- Recovery works; no sticky failure or stale connection pool.
- The gateway error is **not** RFC 7807 problem details. A production ingress should serve a JSON
  problem body (`503 dependency_unavailable`) through a Traefik errors middleware or the ingress
  controller.
- Client retries should treat 502/503 as transient; the web BFF already surfaces a friendly
  "could not be loaded" state.

## Follow-ups

- Add a gateway error-page middleware in production.
- Add a synthetic probe that verifies a service recovers within 30 s.
