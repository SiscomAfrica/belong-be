from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth",
    "django.contrib.contenttypes", "django.contrib.sessions",
    "django.contrib.messages", "django.contrib.staticfiles",
    "corsheaders", "ninja_jwt", "ninja_jwt.token_blacklist",
    "apps.common",
    "apps.users",
    "apps.authentication",
    "apps.audit",
    "apps.funds",
    "apps.market_data",
    "apps.investments",
    "apps.payments",
    "apps.simulation",
    "apps.wishlist",
    "apps.notifications",
    "apps.feed",
    "apps.kyc",
    "apps.pools",
    "apps.ai_profiler", "apps.referrals", "apps.compliance",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION, ASGI_APPLICATION = "config.wsgi.application", "config.asgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://belong:belong@localhost:5432/belong",
    ),
}
DATABASES["default"]["OPTIONS"] = {"pool": {"min_size": 2, "max_size": 4}}
DATABASES["default"].update(CONN_MAX_AGE=0, CONN_HEALTH_CHECKS=True)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE, TIME_ZONE = "en-us", "Africa/Nairobi"
USE_I18N = USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
}

from config.settings.base_celery import *  # noqa: E402, F401, F403
from config.settings.base_logging import *  # noqa: E402, F401, F403
from config.settings.base_payments import *  # noqa: E402, F401, F403
from config.settings.base_kyc import *  # noqa: E402, F401, F403
from config.settings.base_llm import *  # noqa: E402, F401, F403
from config.settings.base_sms import *  # noqa: E402, F401, F403
