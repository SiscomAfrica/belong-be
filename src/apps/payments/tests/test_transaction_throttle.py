from __future__ import annotations

import pytest
from django.core.cache import cache
from django.test import override_settings
from ninja.throttling import AnonRateThrottle, AuthRateThrottle

from config.throttles import (
    AuthEndpointThrottle,
    PaymentInitiationThrottle,
    PaymentReadThrottle,
)

TWELVE_HOURS = 12 * 60 * 60


class Request:
    auth = "user-123"
    META = {"REMOTE_ADDR": "1.2.3.4"}  # noqa: RUF012


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


def test_six_transactions_are_allowed_then_the_seventh_is_not() -> None:
    throttle = PaymentInitiationThrottle("6/12h")

    allowed = [throttle.allow_request(Request()) for _ in range(7)]

    assert allowed == [True] * 6 + [False]


def test_the_window_is_twelve_hours() -> None:
    assert PaymentInitiationThrottle("6/12h").duration == TWELVE_HOURS


def test_status_polling_does_not_consume_the_transaction_allowance() -> None:
    """A top-up polls status up to 40 times; that must not spend a transaction."""
    reads = PaymentReadThrottle("30/m")
    initiations = PaymentInitiationThrottle("6/12h")

    for _ in range(40):
        reads.allow_request(Request())

    assert initiations.allow_request(Request()) is True


def test_ordinary_browsing_does_not_block_a_payment() -> None:
    """The bug: the home screen's requests filled the payment bucket.

    Every AuthRateThrottle shares one cache key, so a router-level limit
    counted requests made anywhere in the API.
    """
    browsing = AuthRateThrottle("1000/h")
    for _ in range(100):
        browsing.allow_request(Request())

    assert PaymentInitiationThrottle("6/12h").allow_request(Request()) is True
    assert PaymentReadThrottle("30/m").allow_request(Request()) is True


def test_every_throttle_counts_into_its_own_bucket() -> None:
    request = Request()
    keys = {
        AuthRateThrottle("1000/h").get_cache_key(request),
        PaymentInitiationThrottle("6/12h").get_cache_key(request),
        PaymentReadThrottle("30/m").get_cache_key(request),
        AnonRateThrottle("100/h").get_cache_key(Anonymous()),
        AuthEndpointThrottle("10/m").get_cache_key(Anonymous()),
    }

    assert len(keys) == 5, "two limits sharing a key corrupt each other's history"


class Anonymous:
    auth = None
    META = {"REMOTE_ADDR": "1.2.3.4"}  # noqa: RUF012


@override_settings(THROTTLE_PAYMENT_INITIATION="6/12h")
def test_limit_is_configurable_without_a_code_change() -> None:
    from config.throttles import payment_initiation_throttles

    assert payment_initiation_throttles()[0].num_requests == 6
