# NeatSprint services (git submodules)

Every component is an independent repository. This directory only contains submodule
pointers; do not add product code here.

| Directory | Repository | Milestone |
| :--- | :--- | :--- |
| `neatsprint-contracts` | API/event schemas | M0 |
| `neatsprint-lib` | Shared Python runtime | M0 |
| `neatsprint-apigw` | Traefik configuration | M0 |
| `neatsprint-iam` | Identity & access | M1 |
| `neatsprint-core` | Tenancy & modules | M1 |
| `neatsprint-task` | Projects, backlog, sprints | M2 |
| `neatsprint-team` | Teams | M2 |
| `neatsprint-worklog` | Time tracking | M3 |
| `neatsprint-monitoring` | Devices, screenshots, privacy | M3 |
| `neatsprint-chat` | Chat | P2 |
| `neatsprint-reports` | Read-model reports | M4 |
| `neatsprint-ai` | AI assistant | P3 |
| `neatsprint-web` | Next.js web app | M0 |
| `neatsprint-desktop` | Tauri agent | M3 |
| `neatsprint-mobile` | Expo app | P2 |

## First clone

```bash
git clone --recurse-submodules https://github.com/neatsprint/neatsprint-platform.git
# or, in an existing clone:
git submodule update --init --recursive
```

## Update

```bash
git submodule update --recursive --remote   # move each to its branch head (review first)
git submodule update --recursive            # move each to the pinned commit
```

## Work in a component

```bash
cd services/neatsprint-iam
git switch -c feat/login
# ... edit, test, commit, push, open PR ...
cd ../..
git add services/neatsprint-iam
git commit -m "chore(submodules): bump iam to v0.3.1 (M1-T06)"
```

Rules:

- Push the component commit before bumping the pin; CI rejects unpushed pins.
- Never edit a file under `services/` from the orchestrator and commit it there.
- `git submodule foreach 'git status --short'` shows dirty components.
- The orchestrator's `main` is the integration point; releases tag the orchestrator.

## Run one service outside Docker

```bash
cd services/neatsprint-task
uv sync
cp .env.example .env
uv run uvicorn neatsprint_task.main:app --reload --port 8000
```

It needs Postgres and Redis; the simplest path is `docker compose up -d postgres redis`.
