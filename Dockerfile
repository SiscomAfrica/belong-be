FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc libpq-dev libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev libcairo2 && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml /tmp/
RUN python -c "import tomllib; \
    d=tomllib.load(open('/tmp/pyproject.toml','rb')); \
    deps=d['project']['dependencies']; \
    dev=d['project'].get('optional-dependencies',{}).get('dev',[]); \
    open('/tmp/reqs.txt','w').write('\n'.join(deps+dev))" && \
    pip install --no-cache-dir -r /tmp/reqs.txt

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

RUN SECRET_KEY=build-placeholder python manage.py collectstatic --noinput 2>/dev/null || true

USER belong

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

CMD ["gunicorn", "config.wsgi:application", "-c", "gunicorn.conf.py"]
