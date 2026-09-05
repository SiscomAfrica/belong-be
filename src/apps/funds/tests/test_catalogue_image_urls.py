from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.cache import cache
from django.test import override_settings
from ninja.testing import TestClient

from apps.funds.models import Fund
from config.urls import api

pytestmark = pytest.mark.django_db

PUBLIC = "https://media.belong.club"
HERO = "hero_images/funds/tech.webp"


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def fund() -> Fund:
    return Fund.objects.create(
        name="Tech Jam",
        slug="tech-jam",
        description="d",
        fund_type="ETF",
        category="TECH",
        risk_level=3,
        currency="USD",
        minimum_investment=Decimal("1000.00"),
        projected_annual_return=Decimal("12.00"),
        effective_annual_yield=Decimal("12.00"),
        annualized_daily_yield=Decimal("0.03"),
        hero_image_url=HERO,
        is_active=True,
    )


@override_settings(PUBLIC_MEDIA_URL=PUBLIC, PUBLIC_MEDIA_BUCKET="belong-media")
def test_fund_list_serves_a_permanent_image_url(fund) -> None:
    """A signature in this URL is what stopped every cache from ever hitting."""
    client = TestClient(api)

    body = client.get("/funds/").json()

    url = body["items"][0]["hero_image_url"]
    assert url == f"{PUBLIC}/{HERO}"
    assert "X-Amz-Signature" not in url


@override_settings(PUBLIC_MEDIA_URL=PUBLIC, PUBLIC_MEDIA_BUCKET="belong-media")
def test_repeated_requests_return_the_identical_url(fund) -> None:
    """Byte-identical across responses, or the phone re-downloads every time."""
    client = TestClient(api)

    first = client.get("/funds/").json()["items"][0]["hero_image_url"]
    second = client.get("/funds/").json()["items"][0]["hero_image_url"]

    assert first == second
