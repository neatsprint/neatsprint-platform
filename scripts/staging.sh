#!/usr/bin/env bash
# Start the local staging profile, seed it and run the staging smoke check.
# Uses .env.staging (ports +1000) and project neatsprint-staging.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is not installed" >&2
  exit 1
fi

if [[ ! -f .env.staging ]]; then
  cp .env.staging.example .env.staging
  echo "Created .env.staging (replace the staging-only secrets before sharing the host)"
fi

ENV_ARGS=(--env-file .env.staging --profile security)

if [[ "${1:-}" == "--down" ]]; then
  docker compose "${ENV_ARGS[@]}" down -v
  exit 0
fi

value() { grep -E "^$1=" .env.staging | head -1 | cut -d= -f2-; }
GATEWAY=$(value GATEWAY_HTTP_PORT)
WEB=$(value WEB_PORT)
IAM=$(value IAM_PORT)
CORE=$(value CORE_PORT)
TOKEN=$(value BOOTSTRAP_TOKEN)

echo "==> Building and starting the staging stack"
docker compose "${ENV_ARGS[@]}" up -d --build

echo "==> Waiting for the gateway"
for _ in $(seq 1 300); do
  if curl -fsS "http://localhost:${GATEWAY}/ping" >/dev/null 2>&1; then break; fi
  sleep 3
done
curl -fsS "http://localhost:${GATEWAY}/ping" >/dev/null

echo "==> Seeding demo data"
CORE_INTERNAL_URL="http://localhost:${CORE}" \
IAM_INTERNAL_URL="http://localhost:${IAM}" \
GATEWAY_URL="http://localhost:${GATEWAY}" \
BOOTSTRAP_TOKEN="${TOKEN}" \
python3 scripts/seed.py

echo "==> Waiting for ClamAV"
for _ in $(seq 1 60); do
  state=$(docker compose "${ENV_ARGS[@]}" ps --format json clamav | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d[0].get("Health","") if isinstance(d,list) else d.get("Health",""))' 2>/dev/null || true)
  [[ "$state" == "healthy" ]] && break
  sleep 10
done

echo "==> Smoke check"
BASE_URL="http://localhost:${GATEWAY}/api/v1" \
WEB_URL="http://localhost:${WEB}" \
SMOKE_EMAIL="owner@acme-labs.com" \
SMOKE_PASSWORD="NeatSprint!2026" \
python3 scripts/smoke/staging_smoke.py

echo ""
echo "Staging is up:"
echo "  Web     http://localhost:${WEB}"
echo "  API     http://localhost:${GATEWAY}/api/v1"
echo "  UAT     run docs/UAT.md against this stack"
