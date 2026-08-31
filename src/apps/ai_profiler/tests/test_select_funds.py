from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from apps.ai_profiler.services.select_funds import band_covers, select_funds

FIXTURES = Path(__file__).resolve().parents[3] / "fixtures"


@dataclass(frozen=True)
class Fund:
    slug: str
    risk_level: int
    category: str


@pytest.fixture(scope="module")
def catalogue() -> list[Fund]:
    """The real catalogue, so these tests fail when inventory actually shifts."""
    raw = json.loads((FIXTURES / "funds.json").read_text())
    entries = raw if isinstance(raw, list) else raw.get("funds", raw)
    return [
        Fund(
            slug=(f := entry.get("fields", entry))["slug"],
            risk_level=int(f["risk_level"]),
            category=f["category"],
        )
        for entry in entries
    ]


def test_never_returns_a_fund_outside_the_band(catalogue) -> None:
    picked = select_funds(
        funds=catalogue, risk_band=[1, 2], category_weights={}, max_funds=5,
    )
    assert picked
    assert all(fund.risk_level <= 2 for fund in picked)


def test_category_weight_decides_the_order(catalogue) -> None:
    picked = select_funds(
        funds=catalogue,
        risk_band=[1, 5],
        category_weights={"DIVERSIFIED": 1.0, "DIVIDEND": 0.5},
        max_funds=2,
    )
    assert [fund.category for fund in picked] == ["DIVERSIFIED", "DIVIDEND"]


def test_respects_max_funds(catalogue) -> None:
    picked = select_funds(
        funds=catalogue, risk_band=[1, 5], category_weights={}, max_funds=3,
    )
    assert len(picked) == 3


def test_selection_is_deterministic(catalogue) -> None:
    args = {"risk_band": [1, 5], "category_weights": {"TECH": 1.0}, "max_funds": 4}
    first = select_funds(funds=catalogue, **args)
    for _ in range(5):
        assert select_funds(funds=catalogue, **args) == first


def test_empty_band_selects_nothing(catalogue) -> None:
    assert select_funds(
        funds=catalogue, risk_band=[], category_weights={}, max_funds=3,
    ) == []


def test_band_covers_reports_unservable_profiles(catalogue) -> None:
    assert band_covers(funds=catalogue, risk_band=[1, 2]) is True
    # No risk-1 fund exists today, so a strictly-1 profile cannot be served.
    assert band_covers(funds=catalogue, risk_band=[1, 1]) is False


def test_catalogue_cannot_serve_a_true_capital_preservation_profile(catalogue) -> None:
    """Documents a real inventory gap rather than hiding it behind an empty list."""
    assert not [fund for fund in catalogue if fund.risk_level == 1]
