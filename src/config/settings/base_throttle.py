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

# How many reverse proxies sit in front of the app.
#
# Without this, django-ninja trusts the entire X-Forwarded-For chain as the
# throttle key. nginx appends the real address to whatever the client sent
# ($proxy_add_x_forwarded_for), so a client supplying its own header gets a
# fresh bucket for every value it invents — and the same throttle class
# guards OTP sending, where each call spends real money on an SMS.
#
# Set to the number of proxies and only their appended address is used, which
# a client cannot influence. One nginx in front means 1.
NINJA_NUM_PROXIES = env.int("NINJA_NUM_PROXIES", default=1)

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

# Public catalogue reads — funds, playlists, market tickers. These are
# declared auth=None, so every request counts as anonymous even from a signed-
# in member, and they all shared the baseline anon bucket. Opening the home
# screen spends four of them, so roughly twenty-five refreshes exhausted the
# limit that is also the last line of defence on OTP. Browsing now has its own
# scope: exhausting it empties the catalogue, never the SMS budget.
THROTTLE_CATALOGUE = env("THROTTLE_CATALOGUE", default="600/h")
