# NeatSprint — Setup & Operator Guide

> **Status**: Approved v1.0 · **Last updated**: 2026-11-22
> **Audience**: Laksiri (operator/owner) · **Scope**: local environment, Google sign-in, CAPTCHA,
> GitHub settings, daily workflow

This is the practical checklist for the work that requires your accounts or judgement. The code is
already in place; these steps connect it to external services.

---

## 1. Local environment (one-time)

### 1.1 Install

| Tool | Version | Check |
| :--- | :--- | :--- |
| Docker Desktop | 4.x+ with Compose v2 | `docker --version` |
| Git | any recent | `git --version` |
| Python | 3.12+ (only for seed/smoke scripts) | `python --version` |
| Node.js | 22 LTS or 24 (web dev only) | `node --version` |
| uv | latest (service dev only) | `uv --version` |
| Rust | stable (desktop, M3) | `cargo --version` |

Docker must be running before bootstrap.

### 1.2 Start the platform

```powershell
git clone --recurse-submodules https://github.com/neatsprint/neatsprint-platform.git
cd neatsprint-platform
./scripts/bootstrap.ps1
```

On macOS/Linux use `./scripts/bootstrap.sh`.

The script:

1. copies `.env.example` → `.env` if missing;
2. builds and starts Postgres, Redis, MinIO, Mailpit, Traefik, nine services and the web app;
3. waits for every `/healthz`;
4. runs `scripts/seed.py` to create **Acme Labs** and six demo users.

If you already have the repository, just run `./scripts/bootstrap.ps1` (add `-NoBuild` for a fast
start, `-NoSeed` to skip seeding).

### 1.3 Open

| Surface | URL |
| :--- | :--- |
| Web app | <http://localhost:3000> |
| Login | <http://localhost:3000/login> |
| Admin users | <http://localhost:3000/admin/users> |
| Roles matrix | <http://localhost:3000/admin/roles> |
| Tenant settings | <http://localhost:3000/admin/settings> |
| API | <http://localhost:8000/api/v1> |
| Traefik dashboard | <http://localhost:8089> |
| MinIO console | <http://localhost:9001> |
| Mailpit (email) | <http://localhost:8025> |

### 1.4 Demo accounts

Password for all: **`NeatSprint!2026`**

| Email | Role |
| :--- | :--- |
| `owner@acme-labs.com` | OWNER |
| `admin@acme-labs.com` | ADMIN |
| `manager@acme-labs.com` | MANAGER |
| `lead@acme-labs.com` | LEAD |
| `member@acme-labs.com` | MEMBER |
| `viewer@acme-labs.com` | VIEWER |

> These are local fixtures. Delete or change them before any shared deployment.

### 1.5 Verify

```powershell
python scripts/smoke-auth.py
```

Everything should print `PASS`, ending with `M1 smoke: PASS`.

---

## 2. Google sign-in (optional, ~10 minutes)

The platform uses **Google Identity Services ID tokens** (no redirect URI flow). Sign-in is
**invitation-first**: a Google account must already have a pending invitation to the tenant.

### 2.1 Create the OAuth client

1. Open <https://console.cloud.google.com/>.
2. Create or select a project (e.g. `NeatSprint`).
3. **APIs & Services → OAuth consent screen**
   - User type: **External** (or Internal for a Workspace-only org).
   - App name: `NeatSprint`, support email: your email.
   - Scopes: `openid`, `email`, `profile` (non-sensitive).
   - Test users: add your own Google address while in testing.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   - Application type: **Web application**.
   - Name: `NeatSprint local`.
   - **Authorized JavaScript origins**: `http://localhost:3000`.
   - Authorized redirect URIs: leave empty (ID-token flow does not use one).
5. Copy the **Client ID** (ends in `.apps.googleusercontent.com`). The client secret is not needed
   for this flow.

### 2.2 Configure

Edit `.env` in the repository root:

```dotenv
GOOGLE_CLIENT_ID=1234567890-abcdef.apps.googleusercontent.com
```

Then recreate IAM and web so both pick up the value:

```powershell
docker compose up -d neatsprint-iam neatsprint-web
```

The login page now shows **Continue with Google** (the button is hidden when the value is empty).

### 2.3 Add the Google user

1. Sign in as the owner with email/password.
2. Go to **Admin → Users → Invite a teammate**.
3. Invite the Google address with the desired role.
4. Sign out, click **Continue with Google**, choose that account.

The first Google sign-in consumes the invitation and creates the account with the invite's roles.

### 2.4 Production

- Add the production origin (e.g. `https://app.neatsprint.com`) to the OAuth client.
- Publish the consent screen when ready; add the privacy policy and terms URLs.
- Set the same `GOOGLE_CLIENT_ID` on IAM and web.

---

## 3. CAPTCHA (optional)

The backend supports **Cloudflare Turnstile** on login, password reset and invitation acceptance.
The web widget is not rendered yet, so **leave `CAPTCHA_SECRET` empty** until the widget ships in
M2. API clients can send `captcha_token` once configured.

When you are ready:

1. Create a Turnstile site at <https://dash.cloudflare.com/> → Turnstile.
2. Add `localhost` and your production domain.
3. Copy the **secret key** into `.env` / IAM:

```dotenv
CAPTCHA_SECRET=0x...
```

4. Recreate IAM: `docker compose up -d neatsprint-iam`.

Without a valid `captcha_token`, auth endpoints return `422 captcha_required`.

---

## 4. Email

- **Local**: Mailpit captures everything at <http://localhost:8025>. Invitation and password-reset
  links are visible there.
- **Production**: set on IAM:

```dotenv
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_FROM="NeatSprint <no-reply@your-domain.com>"
EMAIL_ENABLED=true
```

The sender domain must have SPF/DKIM configured by the provider.

---

## 5. GitHub settings (recommended)

Repositories already exist under `github.com/neatsprint`. Do this once per repository (or automate
with `gh`):

1. **Settings → Branches → Add branch protection rule** for `main`:
   - Require a pull request before merging.
   - Require status checks (`ci / quality`).
   - Require branches to be up to date.
   - Require linear history; disable force pushes and deletions.
2. **Settings → Actions → General**:
   - Allow GitHub Actions.
   - Workflow permissions: read repository contents (write only for release workflows later).
3. **Settings → Environments**: create `staging` and `production`; add required reviewers to
   `production`.
4. **Settings → Secrets and variables → Actions** (when we add deployments):
   - `GHCR_TOKEN`, cloud credentials, `STAGING_URL`, `PRODUCTION_URL`.
5. **Organization → People**: keep the AI account as a collaborator with write access.
6. **Projects**: create a board from the milestones in `docs/MASTER_PLAN.md` (optional, Q10).

The reusable workflows live in `neatsprint-platform/.github/workflows/`; component repositories call
them. No per-repo secrets are needed yet.

---

## 6. Daily workflow

```powershell
# start
docker compose up -d

# status / logs
docker compose ps
docker compose logs -f neatsprint-iam

# reseed (idempotent)
python scripts/seed.py

# verify auth
python scripts/smoke-auth.py

# stop (keeps data)
docker compose down

# stop and wipe local data (destroys demo data and keys)
docker compose down -v
```

After changing `.env`, recreate affected containers (`docker compose up -d <service>`).

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| Port 8080 already in use | another app (e.g. qBittorrent) | dashboard is on **8089**; change `GATEWAY_DASHBOARD_PORT` if needed |
| Port 8000/3000 in use | another stack | stop it or change the port in `.env`, then recreate |
| `429 Too Many Requests` on login | gateway auth bucket (30/min per IP) | wait a minute or restart the gateway in local dev |
| Google button missing | `GOOGLE_CLIENT_ID` empty or web not recreated | set it and `docker compose up -d neatsprint-iam neatsprint-web` |
| Google sign-in says invitation required | invitation-first policy | invite the Google email first |
| Invitation email not received | Mailpit is local-only | open <http://localhost:8025> |
| Object storage errors | MinIO not ready | `docker compose ps minio`; `docker compose logs minio` |
| Migrations did not run | `RUN_MIGRATIONS` not true | check the service env and restart |
| Login works but admin page redirects | access cookie expired and refresh failed | sign in again; check `neatsprint-web` logs |
| Seed says tenant exists | rerunning is safe | it reuses Acme Labs and updates users |
| Want a clean slate | demo data/keys | `docker compose down -v` then bootstrap |

Logs are JSON from services; use `docker compose logs <service> | Select-String "error"`.

---

## 8. Production checklist (before any shared deployment)

1. Replace `BOOTSTRAP_TOKEN` with a strong secret, or unset it to disable seeding endpoints.
2. Provide JWT keys through a secret manager (`JWT_PRIVATE_KEY_PATH` / `JWT_PUBLIC_KEY_PATH`);
   local auto-generation is disabled outside `local`/`ci`.
3. Configure managed Postgres, Redis, S3 and SMTP; run migrations as a pre-deploy job.
4. Set `ENVIRONMENT=production` (disables docs endpoints and requires keys).
5. Enable HTTPS at the ingress; keep HSTS and security headers.
6. Configure Google OAuth production origin and publish the consent screen.
7. Decide on CAPTCHA and wire the web widget.
8. Run `docs/SECURITY.md` §16 verification before opening sign-ups.
9. Review `docs/DEVOPS.md` for backups, alerts and runbooks.

---

## 9. What I need from you next

| # | Decision/action | Blocks |
| :-- | :--- | :--- |
| 1 | Create the Google OAuth client and set `GOOGLE_CLIENT_ID` | Real Google sign-in testing |
| 2 | Decide CAPTCHA now or M2 | Auth hardening |
| 3 | Confirm staging database now or at M5 | Environment provisioning |
| 4 | Review the M2 plan (projects, backlog, sprints, teams) | M2 start |
| 5 | Apply branch protection/environments per §5 | Safe collaboration |

When you have the Google client ID, put it in `.env` and run the two commands in §2.2; then invite
your Google address and test the button.
