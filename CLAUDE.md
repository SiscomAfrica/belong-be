# Belong Backend — Development Standards

## Project Identity
- **App**: Belong — Investment platform for Kenya (CMA & DDPC regulated)
- **Operator**: Tradiam Investments Limited
- **Stack**: Django 5.x + Django Ninja + PostgreSQL + Redis + Celery
- **API consumers**: Kotlin (Android), Swift (iOS), Admin Dashboard
- **This is an API-only backend** — no templates, no server-rendered HTML

## Architecture — Modular Monolith
- **Pattern**: Modular Monolith with Service Layer.
- **Single deployable**: one Django project, one Docker image, one PostgreSQL database.
- **Module boundaries**: each Django app (`apps.<name>`) owns its models, services, selectors, schemas, and API routes. No app reaches into another app's models or ORM directly.
- **Cross-app communication**: always through `services/` and `selectors/` public interfaces. App A calls `apps.users.services.update_user()`, never `User.objects.filter()` from App A.
- **Why monolith**: transactional consistency across domains is critical for fintech (`transaction.atomic()`, `select_for_update()`). Single deployment simplifies regulatory compliance, debugging, and operational overhead at current scale.
- **Why modular**: clean app boundaries make future extraction to microservices possible if scale demands it, without rewriting business logic. Each app can be reasoned about independently.
- **Not microservices**: do not split into separate services prematurely. The cost of distributed transactions, eventual consistency, and inter-service auth is not justified at this stage.

## Hard Rules (Never Violate)

### File Size
- **Maximum 100 lines per file.** No exceptions.
- If a file approaches 100 lines, split it immediately.
- Models: one model per file, collected via `__init__.py` imports.
- Services: one public function per file, or group tightly related functions.
- Schemas: split into `input.py` and `output.py` per module.
- Tests: one test class per file.

### Architecture — Service Layer Pattern
- **Endpoints are thin.** API endpoints do: parse input, call service, return output. Max 5-8 lines of logic per endpoint.
- **Business logic lives in `services/`.** Never in endpoints, models, or schemas.
- **Database reads live in `selectors/`.** Complex querysets and lookups go here.
- **Models are data containers.** No business logic in model methods. Only `__str__`, `Meta`, field declarations, and simple properties (computed from own fields only).
- **Signals live in `signals/`.** Each signal handler in its own file.
- **All service/selector function parameters must be keyword-only** (use `*` as first param). Prevents positional argument bugs.
- **Services NEVER accept `request` as a parameter.** Extract user, data in the endpoint, pass to service.
- **Cross-app communication goes through services/selectors.** App A calls `apps.users.services.update_user()`, never `User.objects.filter()` directly from App A's service.
- **User FK references: always `settings.AUTH_USER_MODEL`**, never `"auth.User"` or direct import.

### Naming Conventions
- Django apps: `apps.<name>` (e.g., `apps.auth`, `apps.funds`)
- App directory: `src/apps/<name>/`
- Config directory: `src/config/`
- Service functions: `verb_noun` (e.g., `create_investment`, `verify_otp`)
- Selector functions: `get_noun` or `list_nouns` (e.g., `get_user_holdings`, `list_active_funds`)
- Schema classes: `<Noun><Action>In` / `<Noun>Out` (e.g., `InvestmentCreateIn`, `InvestmentOut`)
- Router files: `api.py` per app (split into `api_<resource>.py` if over 100 lines)
- Test files: `test_<what>.py` (e.g., `test_services.py`, `test_api.py`)

## Project Structure

```
belong-backend/
  docker-compose.yml
  Dockerfile
  pyproject.toml
  .env.example
  src/
    manage.py
    config/
      __init__.py
      settings/
        __init__.py        # imports based on DJANGO_ENV
        base.py            # shared settings
        local.py           # local dev overrides
        production.py      # production overrides
        test.py            # test overrides
      urls.py
      celery.py
      asgi.py
      wsgi.py
    apps/
      __init__.py
      auth/
        __init__.py
        models/
          __init__.py       # from .otp import OTP etc.
          otp.py
          device.py
        schemas/
          __init__.py
          input.py
          output.py
        services/
          __init__.py
          register.py
          verify_otp.py
          set_pin.py
        selectors/
          __init__.py
          get_user_device.py
        signals/
          __init__.py
          handlers.py
        api.py
        admin.py
        apps.py
        tests/
          __init__.py
          factories.py
          test_services.py
          test_api.py
          test_selectors.py
      # ... same structure for all 15 apps
```

## Django Ninja API Rules

### Router Organization
- One `NinjaAPI` instance in `config/urls.py`.
- Each app exposes a `router` from `apps/<name>/api.py`.
- Mount routers with `api.add_router("/prefix/", "apps.<name>.api.router")`.
- Use string import paths for lazy loading.
- Set `tags` per router for OpenAPI grouping.
- Set `auth` per router (default: JWT for all except public endpoints).

### Schemas (Pydantic)
- All request bodies use `Schema` subclasses — never raw dicts.
- All responses use `Schema` subclasses — never return model instances directly.
- Input schemas go in `schemas/input.py`.
- Output schemas go in `schemas/output.py`.
- Use `from_orm` / `model_config = ConfigDict(from_attributes=True)` for model conversion.
- Never expose internal IDs or sensitive fields in output schemas.

### Authentication
- Use `django-ninja-jwt` for JWT auth.
- Access token: 15 minutes. Refresh token: 30 days.
- Enable token blacklisting via `ninja_jwt.token_blacklist`.
- Set `ROTATE_REFRESH_TOKENS = True` and `BLACKLIST_AFTER_ROTATION = True`.
- Use a dedicated `SIGNING_KEY` separate from `SECRET_KEY`.
- Public endpoints must be explicitly marked with `auth=None`.

### Error Handling
- All errors return: `{"error": {"code": "UPPER_SNAKE", "message": "...", "details": {}}}`.
- `code` is machine-readable (clients switch on `code`, not `message`).
- Services raise `AppError` subclasses — exception handlers format responses.
- Never expose stack traces or internal errors to API consumers.
- Use HTTP status codes correctly: 400 validation, 401 unauth, 403 forbidden, 404 not found, 409 conflict, 422 unprocessable, 429 rate limited, 500 internal.
- Define domain-specific errors: `InsufficientFundsError`, `InvestmentLimitError`, `KYCRequiredError`.

### Throttling
- Global default: `anon: 100/hour`, `user: 1000/hour`.
- Auth endpoints (OTP, login): `10/minute` per IP.
- Payment endpoints: `30/minute` per user.
- Apply at router level via `throttle=` parameter.

### Pagination
- Use `LimitOffsetPagination` as default.
- Default page size: 20. Max page size: 100.
- All list endpoints must be paginated — no unbounded querysets.

## Database Rules (PostgreSQL)

### Connection
- Use Django 5.1+ built-in connection pooling: `OPTIONS.pool` with `min_size: 2, max_size: 4`.
- Set `CONN_MAX_AGE = 0` when using pooling (pool manages lifetime).
- Set `CONN_HEALTH_CHECKS = True`.

### Models
- Every model must have `created_at = DateTimeField(auto_now_add=True)`.
- Every model must have `updated_at = DateTimeField(auto_now=True)`.
- Use `UUIDField(default=uuid.uuid4)` as primary key — never expose auto-increment IDs.
- All monetary values stored as `DecimalField(max_digits=18, decimal_places=2)` in KSh.
- Use `TextChoices` / `IntegerChoices` for enums — never raw strings.
- Add `db_index=True` on fields used in filters and lookups.
- `JSONField`: always `default=dict`, never `default={}` (mutable default bug).
- Add `constraints` in `Meta` for business rules (e.g., unique_together).
- Soft-delete: use `is_active` flag, never `delete()` on financial records.
- Use `AddIndexConcurrently` (not `AddIndex`) for production index additions — requires `atomic = False`.

### Migrations
- One migration per logical change — do not combine unrelated changes.
- Never use `RunPython` with ORM queries in migrations (use raw SQL).
- Always add `reverse_code` to data migrations.
- New nullable columns: add with `null=True`, backfill, then make non-null in a separate migration.
- Never rename columns directly — add new, migrate data, drop old (3-step).

### Query Discipline
- Always use `select_related()` for FK joins in selectors.
- Always use `prefetch_related()` for reverse FK / M2M in selectors.
- Never query inside a loop — use bulk operations (`bulk_create`, `bulk_update`).
- Use `.only()` or `.defer()` for large text/JSON fields not needed.
- Use `F()` expressions for atomic updates, never `obj.field += 1; obj.save()`.
- Use `Q()` for complex filters — never raw SQL unless absolutely necessary.
- Use `.exists()` instead of `.count() > 0` for existence checks.
- Use `select_for_update()` on rows involved in financial transactions to prevent races.
- Use `transaction.atomic()` for any operation modifying multiple related rows.
- Use `django_assert_num_queries` in tests to enforce query counts on critical endpoints.

### Fintech Data Integrity
- All monetary calculations use `decimal.Decimal` in Python — never `float`.
- Every financial mutation creates an immutable `AuditLog` entry (append-only, no updates/deletes).
- Use `select_for_update(skip_locked=True)` in Celery tasks processing financial records.
- Idempotency keys required on all payment creation endpoints.

## Security Rules

### Django Security Settings (Production)
- `DEBUG = False`
- `ALLOWED_HOSTS` — explicit list, never `["*"]`
- `SECRET_KEY` — from environment, minimum 50 chars
- `SECURE_SSL_REDIRECT = True`
- `SECURE_HSTS_SECONDS = 31536000`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- `SECURE_HSTS_PRELOAD = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `X_FRAME_OPTIONS = "DENY"`
- `SECURE_BROWSER_XSS_FILTER = True`

### API Security
- All endpoints require JWT auth unless explicitly public.
- Rate limit all auth endpoints aggressively.
- Hash PINs with bcrypt — never store plaintext.
- OTP codes expire in 5 minutes, single-use, max 3 active per user.
- Webhook endpoints: validate signatures (M-Pesa, Paystack, Smile Identity).
- Use idempotency keys on all payment webhook handlers.
- Never log sensitive data (tokens, PINs, card numbers, PII).
- CORS: allow only known mobile app origins and admin dashboard domain.

### Input Validation
- Pydantic schemas handle type validation automatically.
- Add custom validators for: phone numbers (E.164), email, KSh amounts (positive, max 2 decimals).
- Sanitize all string inputs — strip whitespace, limit length.
- File uploads: validate MIME type, max size (5MB images, 10MB documents).

## Celery & Background Jobs

### Configuration
- Broker: Redis. Result backend: Redis.
- Use `task_always_eager = True` in test settings.
- Serializer: JSON only — never pickle.
- Set `task_acks_late = True` and `task_reject_on_worker_lost = True`.

### Task Design
- All tasks must be idempotent — safe to retry.
- Use `@shared_task(bind=True, name="explicit.name")` — never rely on auto-naming.
- Set explicit `max_retries` and `default_retry_delay` per task.
- Use `retry_backoff=True` and `retry_jitter=True` to prevent thundering herd.
- Set `task_time_limit=300` (hard kill) and `task_soft_time_limit=240` (graceful).
- Use `autoretry_for=(ConnectionError, TimeoutError)` for transient errors.
- Task naming: `apps.<module>.tasks.<verb_noun>` (e.g., `apps.payments.tasks.process_mpesa_callback`).
- One task per file if complex, group simple tasks in a single file (under 100 lines).
- Never pass Django model instances to tasks — pass IDs and re-fetch.
- Log `task_id` and entity IDs in every log entry within a task.

### Scheduled Jobs (Celery Beat)
- Exchange rate fetch: every 60 minutes.
- Recurring investment execution: daily at 06:00 EAT.
- Monthly statement generation: 1st of month at 02:00 EAT.
- Expired OTP cleanup: every 30 minutes.
- Expired token flush: daily at 03:00 EAT.
- Wishlist yield alerts: daily at 08:00 EAT.

## Docker Rules

### Dockerfile
- Base image: `python:3.12-slim` (never Alpine — slow C extension builds).
- Multi-stage build: builder stage installs deps, final stage copies only `/opt/venv`.
- Set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1`.
- Run as non-root user: `useradd -r belong && USER belong`.
- No `apt-get` in final stage — install system deps in builder only.
- Copy `pyproject.toml` and lockfile before source for layer caching.
- `collectstatic` at build time with placeholder `SECRET_KEY`.
- Gunicorn: `(2 * CPU) + 1` workers, `gthread` class, `--worker-tmp-dir /dev/shm`.
- Health check: `curl -f http://localhost:8000/health/`.
- `.dockerignore` must exclude `.env`, `.git`, `__pycache__`, `venv/`, `media/`.

### docker-compose.yml
- Services: `api`, `postgres`, `redis`, `celery-worker`, `celery-beat`.
- **Celery Beat is a singleton** — never scale beyond 1 replica. Duplicates cause double execution.
- Use `depends_on` with `condition: service_healthy` — never bare `depends_on`.
- Use YAML anchors (`x-common-env: &common-env`) to DRY shared env vars.
- Volumes: named volumes for `postgres_data`, `redis_data` — never bind mounts for DBs in prod.
- PostgreSQL: `shm_size: "256mb"`, pin major version (e.g., `postgres:16-alpine`).
- Redis: `--maxmemory 256mb --maxmemory-policy allkeys-lru`.
- `docker-compose.override.yml` for dev (bind mounts, runserver, exposed ports).
- API exposes port 8000 only.

### Environment Files
- `.env.example` committed — contains all keys with placeholder values.
- `.env` in `.gitignore` — never committed.
- Use `django-environ` for parsing.
- Required vars: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `JWT_SIGNING_KEY`, `DJANGO_ENV`.

## Testing Rules

### Framework
- Use `pytest` + `pytest-django`. Never `unittest.TestCase`.
- Use `factory_boy` for test data — never manual `Model.objects.create()` chains.
- One factory per model in `apps/<name>/tests/factories.py`.

### Test Organization
- `test_services.py` — unit tests for service functions.
- `test_api.py` — integration tests for API endpoints.
- `test_selectors.py` — tests for complex queries.
- `test_tasks.py` — tests for Celery tasks (with `task_always_eager`).
- Each test file must stay under 100 lines. Split by feature if needed.

### Test Settings Optimization
- `PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]` — fast hashing in tests.
- `DEFAULT_FILE_STORAGE = "django.core.files.storage.InMemoryStorage"` — no disk I/O.
- `CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}`.
- Use `nplusone` in dev settings with `NPLUSONE_RAISE = True` to crash on N+1 queries.

### Test Patterns
- Use `@pytest.mark.django_db` on tests that touch the database.
- Use Django Ninja `TestClient` for API tests — never Django's `django.test.Client`.
- Mock external services (Smile Identity, M-Pesa, Paystack, LLM) — never hit real APIs.
- Test both success and error paths for every service function.
- Assert specific error codes, not just HTTP status.
- Test every endpoint for: 401 (unauth), 403/404 (wrong user), 422 (validation), and happy path.
- Use `django_assert_num_queries` to enforce query counts on critical endpoints.
- Prefer `factory.build()` over `factory.create()` when DB persistence is not needed (faster).

## Code Quality

### Tooling
- Linter/formatter: `ruff` (replaces black + isort + flake8).
- Type checker: `mypy` with `django-stubs` and `pydantic.mypy` plugins.
- Pre-commit hooks: ruff, mypy, check-merge-conflict, trailing-whitespace, detect-private-key, gitleaks.

### CI Pipeline (in order)
1. `ruff check .` — lint
2. `ruff format --check .` — format verification
3. `mypy .` — type check
4. `python manage.py check --deploy` — Django deployment checks
5. `python manage.py makemigrations --check --dry-run` — no unapplied migration changes
6. `pytest --cov --cov-fail-under=85` — tests with coverage gate
7. `pip-audit` — dependency vulnerability scan

### Ruff Config (pyproject.toml)
- `line-length = 99`
- `target-version = "py312"`
- Select: `["E", "F", "W", "I", "N", "UP", "S", "B", "A", "C4", "DJ", "DTZ", "PIE", "PT", "T20", "SIM", "RET", "PERF", "ERA", "RUF"]`
- `DTZ` enforces timezone-aware datetimes (critical for fintech — catches `datetime.now()`, requires `datetime.now(tz=UTC)`).
- `DJ` enforces Django best practices. `S` enforces security (bandit). `T20` flags `print()`. `PERF` catches performance anti-patterns.
- Per-file-ignores: `"tests/**/*.py" = ["S101", "S106"]`, `"**/migrations/*.py" = ["E501", "ERA"]`.

### Type Hints
- All service functions must have full type annotations.
- All selector functions must have return type annotations.
- Schema classes are typed by Pydantic automatically.
- Use `from __future__ import annotations` in every file.

## Logging

### Setup
- Use `structlog` with Django integration.
- JSON format in production, console format in development.
- Bind `request_id`, `user_id`, `method`, `path` via middleware on every request.
- Add `X-Request-ID` header to responses for client-side correlation.
- Log levels: DEBUG (dev only), INFO (requests, business events), WARNING (recoverable errors), ERROR (unrecoverable), CRITICAL (system down).

### What to Log
- Every API request: method, path, user_id, status, duration.
- Every payment event: rail, amount, status, external_ref.
- Every KYC status change: user_id, old_status, new_status.
- Every Celery task: start, success, failure, retry.
- Never log: tokens, PINs, passwords, full card numbers, PII fields.

## Health Check
- Expose `GET /health/` — unauthenticated, returns `{"status": "healthy", "db": "ok"}` or 503.
- Tests DB connectivity with `SELECT 1`. Used by Docker and load balancers.

## Git & Workflow
- Branch naming: `feature/<app>-<description>`, `fix/<app>-<description>`.
- Commit messages: conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`).
- Every PR must include tests for new/changed functionality.
- No force pushes to `main` or `develop`.
