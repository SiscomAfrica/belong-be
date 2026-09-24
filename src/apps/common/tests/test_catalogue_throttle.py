from __future__ import annotations

import pytest
from django.core.cache import cache

from config.throttles import AuthEndpointThrottle, CatalogueThrottle


class AnonRequest:
    """An unauthenticated caller behind one nginx, as production runs."""

    auth = None

    def __init__(self, client_ip: str, *, forged: str = "") -> None:
        xff = f"{forged}, {client_ip}" if forged else client_ip
        self.META = {"REMOTE_ADDR": "172.18.0.1", "HTTP_X_FORWARDED_FOR": xff}


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


def test_browsing_the_catalogue_does_not_spend_the_otp_budget() -> None:
    """Why this exists: the catalogue routers are auth=None, so even a signed-
    in member's reads counted as anonymous and drained the same bucket that
    rate-limits OTP — where every call sends an SMS that costs real money.
    Opening the home screen spends four of them.
    """
    caller = AnonRequest("41.90.1.1")
    catalogue = CatalogueThrottle("3/h")
    otp = AuthEndpointThrottle("3/h")

    while catalogue.allow_request(caller):
        pass

    assert otp.allow_request(caller) is True


def test_one_client_cannot_exhaust_anothers_bucket() -> None:
    """The throttle keys on the address nginx appends, so two members are
    counted apart. REMOTE_ADDR is the docker bridge for everyone, and keying
    on that would have made a single global bucket for the whole platform.
    """
    throttle = CatalogueThrottle("2/h")
    first = AnonRequest("41.90.1.1")
    second = AnonRequest("41.90.2.2")

    while throttle.allow_request(first):
        pass

    assert throttle.allow_request(second) is True


def test_a_forged_forwarded_header_cannot_mint_a_fresh_bucket() -> None:
    """NUM_PROXIES=1 makes only nginx's appended address count.

    Trusting the whole chain meant a client could send its own
    X-Forwarded-For, which nginx appends to rather than replaces, and get a
    new bucket for every value it invented — defeating the limit entirely.
    """
    throttle = CatalogueThrottle("2/h")
    honest = AnonRequest("41.90.1.1")

    while throttle.allow_request(honest):
        pass

    forged = AnonRequest("41.90.1.1", forged="203.0.113.77")
    assert throttle.allow_request(forged) is False
