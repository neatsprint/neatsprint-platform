#!/usr/bin/env bash
# Bootstrap the NeatSprint local stack.
set -euo pipefail

cd "$(dirname "$0")/.."

step() { printf '\033[36m==> %s\033[0m\n' "$1"; }

command -v docker >/dev/null 2>&1 || { echo "Docker is not installed." >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo "Docker is not running." >&2; exit 1; }

if [ ! -f .env ]; then
  cp .env.example .env
  step "Created .env from .env.example (local development defaults)"
fi

step "Starting the stack"
docker compose up -d --build

step "Waiting for the gateway"
for _ in $(seq 1 120); do
  if curl -fsS http://localhost:8000/ping >/dev/null 2>&1; then break; fi
  sleep 3
done
curl -fsS http://localhost:8000/ping >/dev/null || { echo "Gateway did not become ready." >&2; exit 1; }

failed=""
for entry in iam:8001 core:8002 task:8003 team:8004 worklog:8005 monitoring:8006 chat:8007 reports:8008 ai:8009; do
  name="${entry%%:*}"
  port="${entry##*:}"
  ready=0
  for _ in $(seq 1 45); do
    if curl -fsS "http://localhost:${port}/healthz" >/dev/null 2>&1; then ready=1; break; fi
    sleep 2
  done
  if [ "$ready" = "1" ]; then
    printf '  ok   %-12s :%s\n' "$name" "$port"
  else
    printf '  fail %-12s :%s\n' "$name" "$port"
    failed="$failed $name"
  fi
done

step "NeatSprint is up"
cat <<'EOF'
  Web            http://localhost:3000
  API gateway    http://localhost:8000/api/v1
  Traefik        http://localhost:8089
  MinIO console  http://localhost:9001
  Mailpit        http://localhost:8025
  Grafana        http://localhost:3001   (docker compose --profile observability up -d)
EOF

if [ -n "$failed" ]; then
  echo "Unhealthy:$failed. Inspect with: docker compose logs <service>" >&2
  exit 1
fi
