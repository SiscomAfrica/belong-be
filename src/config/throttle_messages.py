from __future__ import annotations

from django.conf import settings


def transaction_limit() -> int:
    """The number from THROTTLE_PAYMENT_INITIATION, e.g. 6 from "6/12h"."""
    try:
        return int(settings.THROTTLE_PAYMENT_INITIATION.split("/", 1)[0])
    except (AttributeError, ValueError):
        return 0


def humanise_wait(seconds: int | None) -> str:
    if not seconds or seconds < 60:
        return "shortly"
    if seconds < 3600:
        return f"in about {max(1, round(seconds / 60))} minutes"
    return f"in about {max(1, round(seconds / 3600))} hours"


def throttle_message(*, path: str, wait_seconds: int | None) -> str:
    """Explain which limit was reached, in the caller's terms.

    A user who has just tried to send money needs to know whether to retry in a
    minute or tomorrow; "Too many requests." answers neither.
    """
    when = humanise_wait(wait_seconds)

    if path.endswith("/payments/initiate/"):
        limit = transaction_limit()
        return (
            f"You have reached the limit of {limit} transactions in 12 hours. "
            f"Please try again {when}."
        )
    if "/auth/" in path:
        return f"Too many attempts. Please try again {when}."
    return f"Too many requests. Please try again {when}."
