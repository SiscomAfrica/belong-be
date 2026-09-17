from __future__ import annotations

import httpx
from django.conf import settings
from django.core.cache import cache

from apps.payments.exceptions import PaymentProviderError

SANDBOX_URL = "https://sandbox.safaricom.co.ke"
PRODUCTION_URL = "https://api.safaricom.co.ke"

# Named a KEY because it is a cache key, not a credential.
_TOKEN_CACHE_KEY = "mpesa_access_token"  # noqa: S105
# Daraja tokens live for 3600s. Expiring ours slightly early avoids handing a
# token to Safaricom that dies in flight.
_TOKEN_TTL_SECONDS = 3300


def mpesa_base_url() -> str:
    """Daraja host for the configured environment.

    Shared by every M-Pesa rail — STK push and Ratiba standing orders run on
    the same host and the same OAuth credentials.
    """
    if getattr(settings, "MPESA_ENV", "sandbox") == "production":
        return PRODUCTION_URL
    return SANDBOX_URL


def get_mpesa_access_token() -> str:
    """Return a cached Daraja bearer token, fetching one if needed."""
    cached = cache.get(_TOKEN_CACHE_KEY)
    if cached:
        return cached

    url = f"{mpesa_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    try:
        resp = httpx.get(
            url,
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
            timeout=30,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise PaymentProviderError(f"M-Pesa auth failed: {e}") from e

    token = resp.json()["access_token"]
    cache.set(_TOKEN_CACHE_KEY, token, timeout=_TOKEN_TTL_SECONDS)
    return token
