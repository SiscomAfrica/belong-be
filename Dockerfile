FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc libpq-dev libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev libcairo2 && \
    rm -rf /var/lib/apt/lists/*

# Create the venv with the image's own interpreter before uv touches it.
# This is not redundant with `uv sync`: uv will happily download a managed
# Python if none is pinned, and would then build /opt/venv against an
# interpreter that lives outside the venv and is never copied to the final
# stage — leaving a dangling symlink that only fails at container start.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install from the lockfile, not from pyproject.toml.
#
# Resolving pyproject ranges at build time means two builds of the same commit
# can install different versions. The lock pins every transitive dependency,
# so an image built today and one built in six months are identical.
#
# `--frozen` fails the build if uv.lock is out of step with pyproject.toml,
# which turns a silent drift into a loud one. `uv sync` installs only
# [project.dependencies] — the dev extras (pytest, ruff, mypy, django-stubs)
# were previously being shipped to production and no longer are.
COPY --from=ghcr.io/astral-sh/uv:0.10.0 /uv /usr/local/bin/uv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=/opt/venv/bin/python

WORKDIR /build
COPY pyproject.toml uv.lock ./

# --no-install-project: the application is copied into the final stage as
# source, so only its dependencies belong in the venv.
RUN uv sync --frozen --no-install-project --no-dev

# ---------------------------------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 curl libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 libcairo2 libfontconfig1 && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -r -m -s /usr/sbin/nologin belong

COPY --from=builder /opt/venv /opt/venv
COPY src/ /app/src/

WORKDIR /app/src

# Smoke test on its own line, with no `|| true` to swallow it. This is what
# catches a venv built against an interpreter the final stage never received —
# a failure that would otherwise surface only when the container starts.
#
# Only packages that import without Django settings configured belong here.
# `ninja` does not: ninja/conf.py reads settings at import time, so it fails
# outside a configured app and would flag a healthy image as broken.
RUN python -c "import django, celery, httpx, redis; print(django.get_version())"

# collectstatic may legitimately fail (no database, no real settings), so it
# stays non-fatal — but as a separate step, so it cannot mask the check above.
RUN SECRET_KEY=build-placeholder python manage.py collectstatic --noinput 2>/dev/null \
    || echo "collectstatic skipped at build time"

USER belong

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

CMD ["gunicorn", "config.wsgi:application", "-c", "gunicorn.conf.py"]
