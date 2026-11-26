# NeatSprint orchestrator — developer commands.
# On Windows without make, use ./scripts/bootstrap.ps1 directly.

SHELL := /bin/bash
COMPOSE := docker compose

.PHONY: help bootstrap up down stop restart ps logs config test lint e2e clean obs migrate seed staging

help:
	@echo "NeatSprint local development"
	@echo ""
	@echo "  make bootstrap   create .env, build and start everything, wait for health"
	@echo "  make up          start the stack (no rebuild)"
	@echo "  make down        stop all profiles (volumes preserved)"
	@echo "  make clean       stop and delete volumes (destroys local data)"
	@echo "  make ps          show container status"
	@echo "  make logs        tail all logs"
	@echo "  make config      validate docker-compose.yml"
	@echo "  make migrate     run Alembic migrations in every service"
	@echo "  make seed        seed the demo tenant and users"
	@echo "  make staging     start the local staging profile"
	@echo "  make test        run unit tests in every service that has them"
	@echo "  make lint        run ruff/mypy on services and tsc on web"
	@echo "  make e2e         run Playwright (available from M1)"
	@echo "  make obs         start Prometheus + Grafana profile"

bootstrap:
	@./scripts/bootstrap.sh

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) --profile "*" down

stop:
	$(COMPOSE) --profile "*" stop

restart:
	$(COMPOSE) --profile "*" restart

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f --tail=100

config:
	$(COMPOSE) config --quiet && echo "compose config OK"

obs:
	$(COMPOSE) --profile observability up -d prometheus grafana

migrate:
	@for svc in iam core task team worklog monitoring chat reports ai; do \
		echo "== $$svc =="; \
		$(COMPOSE) exec -T neatsprint-$$svc alembic upgrade head || exit 1; \
	done

seed:
	python scripts/seed.py

staging:
	@./scripts/staging.sh

test:
	@for svc in iam core task team worklog monitoring chat reports ai; do \
		if [ -f "services/neatsprint-$$svc/pyproject.toml" ]; then \
			echo "== $$svc =="; (cd "services/neatsprint-$$svc" && uv run pytest) || exit 1; \
		fi; \
	done
	cd services/neatsprint-lib && uv run pytest
	cd services/neatsprint-web && npm test

lint:
	@for svc in iam core task team worklog monitoring chat reports ai; do \
		if [ -f "services/neatsprint-$$svc/pyproject.toml" ]; then \
			echo "== $$svc =="; (cd "services/neatsprint-$$svc" && uv run ruff check . && uv run mypy src) || exit 1; \
		fi; \
	done
	cd services/neatsprint-web && npm run typecheck

e2e:
	@echo "Playwright suite lands in M1"; exit 1

clean:
	$(COMPOSE) --profile "*" down -v --remove-orphans
