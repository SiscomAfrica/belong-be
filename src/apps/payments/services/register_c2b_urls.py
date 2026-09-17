from __future__ import annotations

import httpx
from django.conf import settings

from apps.payments.exceptions import PaymentProviderError
from apps.payments.providers.mpesa_auth import get_mpesa_access_token, mpesa_base_url

_REGISTER_PATH = "/mpesa/c2b/v1/registerurl"


def register_c2b_urls(*, response_type: str = "Completed") -> dict:
    """Tell Safaricom where to post paybill payments.

    Done once per shortcode, not per request — until it is, no confirmation
    ever arrives and Ratiba executions land on the paybill unseen.

    `response_type` decides what happens when our validation URL is
    unreachable: "Completed" lets the payment through, "Cancelled" reverses
    it. Completed is the default because bouncing a customer's contribution
    over an outage of ours is worse than having to reconcile it later.
    """
    base = settings.MPESA_CALLBACK_BASE_URL.rstrip("/")
    payload = {
        "ShortCode": str(settings.MPESA_RATIBA_SHORTCODE),
        "ResponseType": response_type,
        "ConfirmationURL": f"{base}/api/callbacks/c2b/confirmation/",
        "ValidationURL": f"{base}/api/callbacks/c2b/validation/",
    }

    try:
        resp = httpx.post(
            f"{mpesa_base_url()}{_REGISTER_PATH}",
            json=payload,
            headers={"Authorization": f"Bearer {get_mpesa_access_token()}"},
            timeout=30,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise PaymentProviderError(f"C2B URL registration failed: {e}") from e

    return resp.json()
