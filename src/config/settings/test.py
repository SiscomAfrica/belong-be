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

# Eager tasks still resolve a broker and result backend, and the base settings
# point both at Redis. Any test touching a service that queues work — creating
# a notification, for one — otherwise burns ~20 seconds retrying a connection
# that will never come up, then fails on something unrelated to the assertion.
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
CELERY_TASK_STORE_EAGER_RESULT = False

# Dummy R2 credentials so storage clients can be built and requests signed
# entirely offline. The suite never reaches the network — the R2 compatibility
# tests inspect the request botocore *would* send and abort before sending it.
AWS_ACCESS_KEY_ID = "test-key"
AWS_SECRET_ACCESS_KEY = "test-secret"  # noqa: S105
AWS_S3_ENDPOINT_URL = "https://test.r2.cloudflarestorage.com"
PUBLIC_MEDIA_BUCKET = "belong-media-test"
PUBLIC_MEDIA_URL = "https://media.test.invalid"

# Pooling off for tests.
#
# base.py attaches a psycopg connection pool (min_size 2) to any PostgreSQL
# connection. Under the test runner that pool opens connections to a database
# the runner has not created yet, and every test then fails setup with
# PoolTimeout rather than anything that names the cause. Pooling buys nothing
# in a single-threaded test process.
if "OPTIONS" in DATABASES["default"]:  # noqa: F405
    DATABASES["default"]["OPTIONS"].pop("pool", None)  # noqa: F405
