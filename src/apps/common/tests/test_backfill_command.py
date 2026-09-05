from __future__ import annotations

from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import call_command

from apps.common.management.commands import backfill_image_variants as command_module
from apps.funds.models import Fund, FundHolding, Playlist
from apps.funds.selectors.list_catalogue_image_keys import list_catalogue_image_keys

pytestmark = pytest.mark.django_db

HERO = "hero_images/funds/a.jpg"
PLAYLIST = "hero_images/playlists/b.png"
LOGO = "holding_logos/x/c.png"


def make_fund(*, slug: str, hero: str) -> Fund:
    return Fund.objects.create(
        name=slug, slug=slug, description="d", fund_type="ETF", category="TECH",
        risk_level=3, currency="USD", minimum_investment=Decimal("1"),
        projected_annual_return=Decimal("1"), effective_annual_yield=Decimal("1"),
        annualized_daily_yield=Decimal("1"), hero_image_url=hero,
    )


@pytest.fixture
def catalogue() -> None:
    fund = make_fund(slug="t", hero=HERO)
    Playlist.objects.create(name="P", slug="p", hero_image_url=PLAYLIST)
    FundHolding.objects.create(fund=fund, name="H", logo_url=LOGO)


def test_selector_finds_every_stored_key(catalogue) -> None:
    assert list_catalogue_image_keys() == sorted([HERO, PLAYLIST, LOGO])


def test_external_urls_are_skipped(catalogue) -> None:
    """Seed rows point at hosts we do not own and cannot resize."""
    make_fund(slug="x", hero="https://external.example.com/z.png")

    assert all(not k.startswith("http") for k in list_catalogue_image_keys())


def test_generated_variants_are_not_reprocessed(catalogue) -> None:
    """Or a re-run would recurse into its own output."""
    Playlist.objects.create(name="V", slug="v", hero_image_url="hero_images/p/b__160.webp")

    assert "hero_images/p/b__160.webp" not in list_catalogue_image_keys()


def test_command_queues_one_task_per_image(catalogue, monkeypatch) -> None:
    queued: list[str] = []
    monkeypatch.setattr(
        command_module.generate_image_variants,
        "delay",
        lambda key: queued.append(key),
    )

    out = StringIO()
    call_command("backfill_image_variants", stdout=out)

    assert sorted(queued) == sorted([HERO, PLAYLIST, LOGO])
    assert "3 queued." in out.getvalue()


def test_command_is_quiet_when_there_is_nothing_to_do() -> None:
    out = StringIO()
    call_command("backfill_image_variants", stdout=out)

    assert "No catalogue images found." in out.getvalue()
