from __future__ import annotations

from django.conf import settings
from ninja.throttling import AnonRateThrottle, AuthRateThrottle, BaseThrottle

# Every throttle derived from AuthRateThrottle shares the cache key
# `throttle_auth_<user>`, and every AnonRateThrottle shares `throttle_anon_<ip>`.
# Two limits on the same key do not coexist — each reads the other's history and
# writes back a copy truncated to its own window. A router with a 30/m limit
# therefore counted every authenticated request in the whole API, so opening the
# home screen was enough to make the next payment fail with "Too many requests".
#
# Any throttle with a window of its own needs a scope of its own.


class PaymentInitiationThrottle(AuthRateThrottle):
    """Caps how many payments one user may start, per user."""

    scope = "payment_initiation"


class PaymentReadThrottle(AuthRateThrottle):
    """Payment reads, including the status polling that follows a top-up."""

    scope = "payment_read"


class CatalogueThrottle(AnonRateThrottle):
    """Public catalogue reads, kept clear of the baseline anon bucket."""

    scope = "catalogue"


class AuthEndpointThrottle(AnonRateThrottle):
    """Unauthenticated auth endpoints, where each OTP costs a real SMS."""

    scope = "auth_endpoint"


def payment_initiation_throttles() -> list[BaseThrottle]:
    return [PaymentInitiationThrottle(settings.THROTTLE_PAYMENT_INITIATION)]


def payment_read_throttles() -> list[BaseThrottle]:
    return [PaymentReadThrottle(settings.THROTTLE_PAYMENTS)]


def catalogue_throttles() -> list[BaseThrottle]:
    """Anonymous browsing gets its own scope; signed-in reads keep the
    per-user limit, since these routers carry both."""
    return [
        CatalogueThrottle(settings.THROTTLE_CATALOGUE),
        AuthRateThrottle(settings.THROTTLE_USER),
    ]


def auth_endpoint_throttles() -> list[BaseThrottle]:
    return [AuthEndpointThrottle(settings.THROTTLE_AUTH)]


def default_throttles() -> list[BaseThrottle]:
    """Baseline limits applied to every endpoint.

    Routers that need their own limit declare it, which replaces this rather
    than adding to it.
    """
    return [
        AnonRateThrottle(settings.THROTTLE_ANON),
        AuthRateThrottle(settings.THROTTLE_USER),
    ]
