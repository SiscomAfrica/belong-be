.PHONY: up down build migrate makemigrations shell test lint format logs \
        createsuperuser seed-profiles sync-playlists release \
        prod-build prod-up prod-release prod-migrate prod-logs prod-ps

COMPOSE = docker compose
COMPOSE_PROD = docker compose -f docker-compose.prod.yml
MANAGE = python manage.py

# ---------------------------------------------------------------- development

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

migrate:
	$(COMPOSE) exec api $(MANAGE) migrate

makemigrations:
	$(COMPOSE) exec api $(MANAGE) makemigrations

shell:
	$(COMPOSE) exec api $(MANAGE) shell

test:
	$(COMPOSE) exec api pytest --cov=apps --cov-report=term-missing

lint:
	$(COMPOSE) exec api ruff check src/

format:
	$(COMPOSE) exec api ruff format src/

logs:
	$(COMPOSE) logs -f

createsuperuser:
	$(COMPOSE) exec api $(MANAGE) createsuperuser

seed-profiles:
	$(COMPOSE) exec api $(MANAGE) seed_profiles

sync-playlists:
	$(COMPOSE) exec api $(MANAGE) sync_playlists

# Schema, then profile centroids and criteria, then the playlists derived from
# them. Order matters: profile matching has no candidates until seed_profiles
# has run, and playlists cannot be composed until the criteria exist.
release: migrate seed-profiles sync-playlists

# ----------------------------------------------------------------- production

prod-build:
	$(COMPOSE_PROD) build

prod-up:
	$(COMPOSE_PROD) up -d

prod-migrate:
	$(COMPOSE_PROD) run --rm api $(MANAGE) migrate

# Full production release.
#
# Schema and seed run on a throwaway container while the API is still serving
# the old image, so there is no window where the new code is live without the
# data it needs. Completing onboarding raises a 500 if seed_profiles has not
# run, which makes this ordering a requirement rather than a tidiness habit.
prod-release:
	$(COMPOSE_PROD) build
	$(COMPOSE_PROD) up -d postgres redis
	$(COMPOSE_PROD) run --rm api $(MANAGE) migrate
	$(COMPOSE_PROD) run --rm api $(MANAGE) seed_profiles
	$(COMPOSE_PROD) run --rm api $(MANAGE) sync_playlists
	$(COMPOSE_PROD) up -d
	$(COMPOSE_PROD) ps

prod-logs:
	$(COMPOSE_PROD) logs -f

prod-ps:
	$(COMPOSE_PROD) ps
