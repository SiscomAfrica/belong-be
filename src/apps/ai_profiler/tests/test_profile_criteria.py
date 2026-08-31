from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from statistics import mean

import pytest

from apps.ai_profiler.rubric import CENTROIDS, ORDINAL_KEYS
from apps.ai_profiler.services.select_funds import select_funds
from apps.funds.models.enums import FundCategory, RiskLevel

FIXTURES = Path(__file__).resolve().parents[3] / "fixtures"
RISK_ORDER = ["CONSERVATIVE", "MODERATE", "INTERMEDIATE", "AGGRESSIVE", "HIGH_RISK"]


@dataclass(frozen=True)
class Fund:
    slug: str
    risk_level: int
    category: str


@pytest.fixture(scope="module")
def catalogue() -> list[Fund]:
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


@pytest.fixture(scope="module")
def profiles() -> list[dict]:
    return json.loads((FIXTURES / "profile_templates.json").read_text())["profiles"]


def test_every_category_weight_names_a_real_category(profiles) -> None:
    """A typo here fails silently — the fund just never gets weighted."""
    valid = set(FundCategory.values)
    for profile in profiles:
        unknown = set(profile["category_weights"]) - valid
        assert not unknown, f"{profile['investor_type']}: unknown categories {unknown}"


def test_every_risk_band_is_within_the_scale(profiles) -> None:
    valid = set(RiskLevel.values)
    for profile in profiles:
        low, high = profile["risk_band"]
        assert low in valid
        assert high in valid
        assert low <= high


def test_centroids_match_the_rubric(profiles) -> None:
    for profile in profiles:
        assert profile["centroid"] == CENTROIDS[profile["investor_type"]]


def test_every_centroid_covers_every_ordinal_behaviour(profiles) -> None:
    for profile in profiles:
        assert set(profile["centroid"]) == set(ORDINAL_KEYS)


def test_risk_bands_ascend_with_the_profile_order(profiles) -> None:
    ordered = sorted(profiles, key=lambda p: RISK_ORDER.index(p["investor_type"]))
    bands = [p["risk_band"] for p in ordered]
    assert bands == sorted(bands)


def test_criteria_produce_a_non_inverted_ordering(catalogue, profiles) -> None:
    """The real guard: composed playlists must not invert, on today's catalogue."""
    by_type = {p["investor_type"]: p for p in profiles}
    means = []

    for investor_type in RISK_ORDER:
        profile = by_type[investor_type]
        chosen = select_funds(
            funds=catalogue,
            risk_band=profile["risk_band"],
            category_weights=profile["category_weights"],
            max_funds=profile["max_funds"],
        )
        assert chosen, f"{investor_type} composes to an empty playlist"
        means.append((investor_type, mean(f.risk_level for f in chosen)))

    for (lower, low_mean), (higher, high_mean) in pairwise(means):
        assert low_mean <= high_mean, (
            f"{lower} composes to risk {low_mean:.2f} but {higher} to {high_mean:.2f}"
        )
