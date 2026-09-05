from __future__ import annotations

from config.settings.base import *  # noqa: F401, F403

DEBUG = False

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Dummy R2 credentials so storage clients can be built and requests signed
# entirely offline. The suite never reaches the network — the R2 compatibility
# tests inspect the request botocore *would* send and abort before sending it.
AWS_ACCESS_KEY_ID = "test-key"
AWS_SECRET_ACCESS_KEY = "test-secret"  # noqa: S105
AWS_S3_ENDPOINT_URL = "https://test.r2.cloudflarestorage.com"
PUBLIC_MEDIA_BUCKET = "belong-media-test"
PUBLIC_MEDIA_URL = "https://media.test.invalid"
