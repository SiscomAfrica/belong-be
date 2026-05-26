from __future__ import annotations

from config.settings.base import *  # noqa: F401, F403

DEBUG = True

INSTALLED_APPS += ["django_extensions"]  # type: ignore[name-defined]  # noqa: F405

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
}
