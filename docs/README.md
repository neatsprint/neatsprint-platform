# NeatSprint — Documentation Index

> **Status**: Approved v1.0 · **Last updated**: 2026-11-21

This directory is the **authoritative** documentation set. The `documents/` directory at the
repository root is the original input architecture and is kept as read-only reference.

---

## 1. Start Here

| If you want to… | Read |
| :--- | :--- |
| Understand what we are building and why | [`SCOPE.md`](SCOPE.md) |
| Know the order of work and current progress | [`MASTER_PLAN.md`](MASTER_PLAN.md) |
| Pick up the next task | [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md) |
| Know how a change will be verified | [`TEST_PLAN.md`](TEST_PLAN.md) |
| Understand the system design | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Change a database schema | [`DATA_MODEL.md`](DATA_MODEL.md) |
| Add or change an endpoint | [`API_SPEC.md`](API_SPEC.md) |
| Touch auth, monitoring or privacy | [`SECURITY.md`](SECURITY.md) |
| Design or review a screen | [`UI_UX_DESIGN.md`](UI_UX_DESIGN.md) |
| Set up CI, deploy or operate | [`DEVOPS.md`](DEVOPS.md) |
| Create repositories or work with submodules | [`REPOSITORIES.md`](REPOSITORIES.md) |
| Know why a choice was made | [`DECISIONS.md`](DECISIONS.md) |
| Understand a term | [`GLOSSARY.md`](GLOSSARY.md) |
| Contribute code | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Understand the AI-agent process | [`../AGENTS.md`](../AGENTS.md) |

---

## 2. Document Map

| Document | Covers | Owner | Status |
| :--- | :--- | :--- | :--- |
| [`SCOPE.md`](SCOPE.md) | Vision, personas, in/out of scope, requirements `FR-*`/`NFR-*`, acceptance | Laksiri | Approved v1.0 |
| [`MASTER_PLAN.md`](MASTER_PLAN.md) | Phases M0–M5/P2/P3, workstreams, gates, risks, effort | Laksiri | Approved v1.0 |
| [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md) | Task-level backlog with checkboxes and IDs | OpenCade | Approved v1.0 |
| [`TEST_PLAN.md`](TEST_PLAN.md) | Strategy, suites `TS-*`, cases `TC-*`, security/perf/accessibility | OpenCade | Approved v1.0 |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Context, containers, services, flows, failure modes | OpenCade | Approved v1.0 |
| [`DATA_MODEL.md`](DATA_MODEL.md) | Per-service schemas, constraints, indexes, retention | OpenCade | Approved v1.0 |
| [`API_SPEC.md`](API_SPEC.md) | Conventions, endpoint catalogue, payloads, governance | OpenCade | Approved v1.0 |
| [`SECURITY.md`](SECURITY.md) | Threat model, authz matrix, privacy model, compliance | OpenCade | Approved v1.0 |
| [`UI_UX_DESIGN.md`](UI_UX_DESIGN.md) | Design system, screens, flows, copy, accessibility | OpenCade | Approved v1.0 |
| [`DEVOPS.md`](DEVOPS.md) | Environments, CI/CD, observability, backup/DR | OpenCade | Approved v1.0 |
| [`REPOSITORIES.md`](REPOSITORIES.md) | 15 repositories, creation order, submodule workflow | OpenCade | Approved v1.0 |
| [`DECISIONS.md`](DECISIONS.md) | ADR-001…017 | Laksiri (approve) | Living |
| [`GLOSSARY.md`](GLOSSARY.md) | Shared vocabulary and naming conventions | OpenCade | Living |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Branching, standards, PR checklist, rules | OpenCade | Living |
| `CHANGELOG.md` | Delivered changes | OpenCade | Living |
| `RUNBOOKS.md` | Operational procedures | OpenCade | Created at M0, completed M5 |
| `RELEASE_NOTES.md` | Version history | OpenCade | Created at M5 |

---

## 3. Conventions

### 3.1 Status header

Every document begins with a blockquote:

```markdown
> **Status**: Approved v1.0 · **Version**: 1.0 · **Last updated**: YYYY-MM-DD
> **Owner**: … · **Author**: … · **Supersedes**: … · **Related**: …
```

Status values: `Draft`, `Draft for review`, `Approved`, `Living`, `Superseded`, `Deferred`.

### 3.2 Identifiers

| Prefix | Meaning | Example |
| :--- | :--- | :--- |
| `FR-<DOMAIN>-nn` | Functional requirement | `FR-MON-04` |
| `NFR-<AREA>-nn` | Non-functional requirement | `NFR-SEC-02` |
| `M<milestone>-T<nn>` | Development task | `M3-T15` |
| `M<milestone>-E<nn>` | Epic | `M3-E2` |
| `TS-nn` | Test suite | `TS-06` |
| `TC-<AREA>-nnn` | Test case | `TC-MON-003` |
| `ADR-nnn` | Decision record | `ADR-005` |
| `R-nn` | Risk | `R-02` |
| `T-nn` | Threat | `T-07` |
| `G<n>` | Quality gate | `G3` |
| `S-nn` | Screen | `S-13` |

IDs are stable. Never renumber; append and mark obsolete entries instead.

### 3.3 Traceability

Every requirement must appear in the traceability tables (`SCOPE.md` §11, `TEST_PLAN.md` §10) and
in at least one development task. A requirement without a task is a planning defect.

### 3.4 Checkboxes

- `- [ ]` planned
- `- [~]` in progress (use text, not a special markdown syntax)
- `- [x]` done, with evidence

Ticking a box without evidence is treated as a false status and will be reverted.

### 3.5 Diagrams

- Mermaid only (renders in GitHub and most editors).
- One concept per diagram; label edges with verbs.
- Keep node names short; put detail in tables beside the diagram.
- Do not embed screenshot images for architecture; use diagrams that live in text.

### 3.6 Dates and numbers

- Dates `YYYY-MM-DD`; timestamps ISO 8601 UTC.
- Durations in seconds in the API; humanised (`1h 24m`) in the UI.
- Currency not used in MVP.

---

## 4. Change Process

| Change type | Process |
| :--- | :--- |
| Typo / clarity | Direct commit, `docs: …` |
| Requirement change | Update `SCOPE.md`, add a scope-change note, update plans and tests |
| Architecture change | ADR first (`DECISIONS.md`), then design documents |
| API change | Contract repo first, then `API_SPEC.md`, then code |
| Screen change | `UI_UX_DESIGN.md` first, then implementation |
| Plan change | Update `DEVELOPMENT_PLAN.md` and its change log; note in `MASTER_PLAN.md` |
| Scope expansion after MVP freeze | Icebox by default; requires Laksiri's explicit approval |

---

## 5. Relationship to `documents/`

| `documents/` (reference) | `docs/` (authoritative) |
| :--- | :--- |
| Original input set, 24 files | Refined, consolidated, maintained set |
| Frozen; do not edit | Living; edit in place |
| Overlapping/inconsistent claims | Single canonical position per topic |
| No IDs or checkboxes | Requirement/task/test IDs, progress tracking |

Mapping of the reference files:

| Reference | Absorbed into |
| :--- | :--- |
| `scope.md` | `SCOPE.md` |
| `tech-design.md`, `step1`, `step3` | `ARCHITECTURE.md` |
| `step2-mvp-roadmap.md` | `MASTER_PLAN.md` |
| `step4-api-gateway-architecture.md` | `ARCHITECTURE.md` §3, `DEVOPS.md` |
| `step5-deployment-and-cicd-architecture.md` | `DEVOPS.md` |
| `step6-er-diagrams.md`, `step7-…schemas.md` | `DATA_MODEL.md` |
| `step8-security-and-privacy-model.md` | `SECURITY.md` |
| `step9-authorization-enforcement-flow.md` | `SECURITY.md` §4, `ARCHITECTURE.md` §4 |
| `step10-rbac-definitions.md` | `SECURITY.md` §4.3 |
| `step11-data-retention-policy.md` | `SECURITY.md` §12, `DATA_MODEL.md` §13 |
| `step12-api-contracts.md`, `step13-detailed-api-spec.md` | `API_SPEC.md` |
| `step14-end-to-end-flows.md` | `ARCHITECTURE.md` §4–6 |
| `step15-desktop-app-architecture.md`, `step16-…` | `ARCHITECTURE.md` §6, `SECURITY.md` §9 |
| `step17-mobile-app-architecture.md` | `ARCHITECTURE.md` §8 |
| `step18-web-app-architecture.md` | `UI_UX_DESIGN.md`, `ARCHITECTURE.md` §3 |
| `step19-reports-architecture.md`, `step20-…` | `ARCHITECTURE.md` §7, `DATA_MODEL.md` §8 |
| `step21-ai-architecture.md`, `step22-…` | `ARCHITECTURE.md` §9, `SECURITY.md` §8 |

---

## 6. Review Checklist for This Documentation Set

- [ ] Scope boundaries match Laksiri's intent
- [ ] Open questions in `SCOPE.md` §12 answered
- [ ] ADR-001, 005, 010, 012, 015 confirmed
- [ ] Repository names and org confirmed in `REPOSITORIES.md` §9
- [ ] Milestone sequence and effort accepted
- [ ] Design system direction accepted (colours, type, layout)

---

**End of Index**
