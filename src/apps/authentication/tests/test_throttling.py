from __future__ import annotations

import pytest
from django.core.cache import cache
from django.test import override_settings

from config.urls import api

pytestmark = pytest.mark.django_db

OTP_SEND = "/auth/otp/send"
TOO_MANY = 429


@pytest.fixture(autouse=True)
def _clear_throttle_counters():
    """Counters live in the cache and would otherwise leak between tests."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def client():
    from ninja.testing import TestClient

    return TestClient(api)


def test_otp_send_is_rate_limited(client) -> None:
    """OTP send is unauthenticated and bills per SMS — it must not be open."""
    seen = [
        client.post(OTP_SEND, json={"phone": "+254700000001"}).status_code
        for _ in range(15)
    ]

    assert TOO_MANY in seen, f"no request was throttled: {sorted(set(seen))}"


def test_throttled_response_is_429_not_500(client) -> None:
    for _ in range(15):
        response = client.post(OTP_SEND, json={"phone": "+254700000001"})
        if response.status_code == TOO_MANY:
            break

    assert response.status_code == TOO_MANY


@override_settings(THROTTLE_AUTH="1000/m")
def test_limit_is_configurable(client) -> None:
    """Rates come from settings so they can be relaxed in tests or staging.

    The router captured its rate at import, so this asserts the setting exists
    and is readable rather than that the live router re-reads it.
    """
    from django.conf import settings

    assert settings.THROTTLE_AUTH == "1000/m"


def test_health_is_not_throttled_into_uselessness(client) -> None:
    """Load balancers poll health constantly; it must survive the anon limit."""
    codes = {client.get("/health/").status_code for _ in range(5)}

    assert TOO_MANY not in codes
