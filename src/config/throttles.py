from __future__ import annotations

from django.conf import settings
from ninja.throttling import AnonRateThrottle, AuthRateThrottle, BaseThrottle


def default_throttles() -> list[BaseThrottle]:
    """Baseline limits applied to every endpoint.

    Routers that need to be stricter — auth, payments — declare their own,
    which replaces this rather than adding to it.
    """
    return [
        AnonRateThrottle(settings.THROTTLE_ANON),
        AuthRateThrottle(settings.THROTTLE_USER),
    ]
