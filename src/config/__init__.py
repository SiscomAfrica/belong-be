from __future__ import annotations

# Importing the app here is what makes it Celery's *current* app for every
# process that loads Django, not just the worker.
#
# `celery -A config.celery worker` imports it by name, so the worker and beat
# were always configured. The web process was not: nothing imported this
# module, so `shared_task(...).delay()` inside a request bound to Celery's
# unconfigured fallback app and published to amqp://localhost — a broker this
# stack does not run — instead of the project's Redis.
from config.celery import app as celery_app

__all__ = ["celery_app"]
