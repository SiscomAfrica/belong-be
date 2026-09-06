from __future__ import annotations

import environ

env = environ.Env()

# Throttle counters live in the cache, so the backend has to be shared across
# processes. With Django's default LocMemCache each gunicorn worker keeps its
# own counts — two workers means double the intended rate, and every worker
# recycle resets them. Redis is already running for Celery; this uses a
# separate database index on the same instance.
#
# Note the instance runs `volatile-lru`, so only keys with a TTL are evicted.
# Throttle counters expire; Celery broker messages do not.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("CACHE_URL", default="redis://localhost:6379/3"),
    },
}

# Request rate limits. Auth is the one that matters most: OTP send is
# unauthenticated and costs real money per call via Tilil, which makes it the
# cheapest endpoint in the system to abuse.
THROTTLE_ANON = env("THROTTLE_ANON", default="100/h")
THROTTLE_USER = env("THROTTLE_USER", default="1000/h")
THROTTLE_AUTH = env("THROTTLE_AUTH", default="10/m")
# Applies to the whole payments router: reads, status polling, everything.
# Deliberately generous, because it is not what limits how much money moves.
THROTTLE_PAYMENTS = env("THROTTLE_PAYMENTS", default="30/m")

# How many payments one user may *start*. This is the limit that matters, and
# it is counted separately from reads: the app polls payment status up to 40
# times per top-up, so a shared bucket was exhausted by a single successful
# transaction and the next attempt was refused.
#
# Sliding window, not a fixed one — with a fixed reset a user could start 6
# just before the boundary and 6 just after.
THROTTLE_PAYMENT_INITIATION = env("THROTTLE_PAYMENT_INITIATION", default="6/12h")
