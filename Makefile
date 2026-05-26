.PHONY: up down build migrate makemigrations shell test lint format logs createsuperuser

COMPOSE = docker compose

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

migrate:
	$(COMPOSE) exec api python manage.py migrate

makemigrations:
	$(COMPOSE) exec api python manage.py makemigrations

shell:
	$(COMPOSE) exec api python manage.py shell

test:
	$(COMPOSE) exec api pytest --cov=apps --cov-report=term-missing

lint:
	$(COMPOSE) exec api ruff check src/

format:
	$(COMPOSE) exec api ruff format src/

logs:
	$(COMPOSE) logs -f

createsuperuser:
	$(COMPOSE) exec api python manage.py createsuperuser
