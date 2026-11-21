# Contributing to NeatSprint

> **Status**: Active · **Last updated**: 2026-11-21
> **Audience**: Laksiri, AI agents, and any future contributor

---

## 1. Before You Start

1. Read `AGENTS.md` (process) and `docs/SCOPE.md` (what matters).
2. Find the next unchecked task in `docs/DEVELOPMENT_PLAN.md`.
3. Check `docs/DECISIONS.md` for settled choices — do not reopen them silently.
4. For anything security-, privacy- or contract-related, read the relevant section of
   `docs/SECURITY.md` or `docs/API_SPEC.md` first.

---

## 2. Local Setup

```bash
git clone --recurse-submodules https://github.com/neatsprint/neatsprint-platform.git
cd neatsprint-platform
./scripts/bootstrap.ps1          # Windows (or ./scripts/bootstrap.sh)
docker compose up -d --build
```

- Web: <http://localhost:3000>
- API: <http://localhost:8000/api/v1>
- Traefik dashboard: <http://localhost:8089>
- MinIO console: <http://localhost:9001>
- Mailpit: <http://localhost:8025>
- Grafana (observability profile): <http://localhost:3001>

Demo credentials are printed by the seed script and documented in `services/README.md`.

### 2.1 Working in a service

```bash
cd services/neatsprint-iam
uv sync
uv run pytest
uv run ruff check .
uv run mypy src
```

### 2.2 Working on the web app

```bash
cd services/neatsprint-web
pnpm install
pnpm dev
pnpm lint && pnpm tsc --noEmit && pnpm test
```

---

## 3. Branching & Commits

- Branches: `feat/<area>-<slug>`, `fix/<area>-<slug>`, `chore/<slug>`, `docs/<slug>`.
- Conventional Commits, imperative, ≤ 72 chars in the subject.
- Reference the plan task: `feat(worklog): idempotent offline sync (M3-T05)`.
- Squash-merge to `main`. Never force-push `main` or a tag.
- One logical change per PR. Refactors and behaviour changes go in separate PRs.

Examples:

```text
feat(iam): rotate refresh tokens with reuse detection (M1-T08)
fix(monitoring): refuse manager access to pending screenshots (M3-T14)
docs(scope): clarify one-tenant-per-user assumption
chore(submodules): bump task to v0.4.2
```

---

## 4. Pull Request Checklist

Copy into the PR description:

```markdown
## What
- …

## Why
- Requirement: FR-…
- Task: M…

## How
- …

## Verification
- [ ] Unit tests
- [ ] Integration tests
- [ ] Contract tests (if API changed)
- [ ] Manual check: …

## Risk
- Tenant isolation: scoped? yes/no
- Permission: required permission + test
- Migration: none / name
- Breaking change: no / yes (ADR)
```

Reviewer focuses on: correctness, tenant scoping, permission enforcement, error codes, migration
safety, test quality, docs.

---

## 5. Coding Standards

### Python

- Ruff for lint + format, mypy strict on `src/`.
- Routers: validation + dependency wiring only. Domain logic in `core/`. SQL in `db/`.
- No f-strings in SQL. No ORM objects returned from routers — map to Pydantic schemas.
- Exceptions: raise typed domain errors that map to RFC 7807 problem details.
- Logging: structured, `logger.info("event", extra={...})`, no PII, no tokens.
- Time: inject a clock; never call `datetime.now()` inside domain logic.

### TypeScript

- `strict: true`, no `any` without a justifying comment, no non-null assertions in new code.
- Server state via TanStack Query; local UI state via Zustand. No global fetch wrappers duplicating
  the generated client.
- Components: small, typed props, no inline hex colours (use tokens), no business logic in render.
- Accessibility attributes are part of the definition of done, not a follow-up.

### SQL / Migrations

- Forward-only, descriptive names, no data manipulation in schema migrations.
- Add indexes with the query that needs them in the PR description.
- Never edit a merged migration.

### Contracts

- The OpenAPI/AsyncAPI change lands in `neatsprint-contracts` first.
- Additive changes only within `/api/v1`. Breaking changes need a major version and an ADR.
- Every error `code` is documented and tested.

---

## 6. Testing Requirements

| Change | Required tests |
| :--- | :--- |
| New endpoint | Unit + integration + authz matrix entry + isolation case |
| New domain rule | Unit tests including invalid paths |
| Bug fix | Regression test that fails without the fix |
| Schema change | Migration up test + repository test |
| UI screen | Component test + loading/empty/error states + axe |
| Security control | Negative test proving the bypass is blocked |

Run `make test` before pushing. CI is the authority; a red pipeline blocks merge.

---

## 7. Documentation Rules

- Behaviour change ⇒ update the matching document in `docs/` in the **same PR**.
- New decision ⇒ ADR in `docs/DECISIONS.md` (context, decision, consequences, alternatives).
- New term ⇒ `docs/GLOSSARY.md`.
- New screen or component ⇒ `docs/UI_UX_DESIGN.md`.
- New endpoint ⇒ `docs/API_SPEC.md` (catalogue) and the contract repo.
- Tick checkboxes only when the Definition of Done is met.
- Keep `docs/CHANGELOG.md` current for user-visible changes.

---

## 8. Submodule Workflow

```bash
# after cloning
git submodule update --init --recursive

# work
cd services/neatsprint-task
git switch -c feat/ranking
# ... commit, push, open PR, merge ...

# bump the pin from the orchestrator
cd ../..
git add services/neatsprint-task
git commit -m "chore(submodules): bump task to v0.5.0 (M2-T05)"
```

Rules:

- Push the submodule commit before bumping the pin.
- Never leave a dirty submodule when committing the orchestrator.
- `git submodule foreach` is your friend for bulk status checks.

---

## 9. Environment & Secrets

- Copy `.env.example` to `.env`; never commit `.env`.
- Local dev keys are generated by `scripts/bootstrap` and are obviously non-production.
- Shared environments receive secrets from the secret manager only.
- If you suspect a secret was committed: rotate it first, then remove it from history.

---

## 10. Security & Privacy Rules for Contributors

**Never**:

- Add silent capture, hidden processes, or disable the recording indicator.
- Log screenshots, tokens, passwords, or PII.
- Query without a tenant scope.
- Return `403` for a foreign-tenant ID (return `404`).
- Ship an endpoint without a declared permission.
- Add analytics or third-party scripts that see tenant data.
- Keep a deleted blob or derived embedding "just in case".

**Always**:

- Treat deletion as irreversible.
- Ask "who can see this?" before adding a field to an API response.
- Prefer 404 for existence privacy.
- Add a test for the negative path.
- Record a decision when you deviate.

---

## 11. Reporting a Security Issue

Do not open a public issue. Email the maintainer listed in `SECURITY.md` (repository file) or use
GitHub private vulnerability reporting. Expect acknowledgement within 48 hours. Do not test against
production tenants without written permission.

---

## 12. Licence

Contributions are accepted under **AGPLv3**. By opening a PR you confirm you have the right to
submit the code under that licence. Do not copy code with incompatible licensing.

---

**End of Contributing Guide**
