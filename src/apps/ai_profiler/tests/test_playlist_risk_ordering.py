from __future__ import annotations

import json
from itertools import pairwise
from pathlib import Path
from statistics import mean

import pytest

FIXTURES = Path(__file__).resolve().parents[3] / "fixtures"

# Profiles ordered from least to most risk-tolerant. A profile's playlist must
# never carry more average risk than the playlist of a more risk-tolerant one.
RISK_ORDER = [
    "CONSERVATIVE",
    "MODERATE",
    "INTERMEDIATE",
    "AGGRESSIVE",
    "HIGH_RISK",
]


@pytest.fixture(scope="module")
def fund_risk() -> dict[str, int]:
    raw = json.loads((FIXTURES / "funds.json").read_text())
    funds = raw if isinstance(raw, list) else raw.get("funds", raw)
    return {
        f.get("fields", f)["slug"]: int(f.get("fields", f)["risk_level"])
        for f in funds
    }


@pytest.fixture(scope="module")
def templates() -> dict:
    return json.loads((FIXTURES / "profile_templates.json").read_text())


def _playlist_risks(templates: dict, fund_risk: dict[str, int]) -> dict[str, list[int]]:
    by_slug = {p["slug"]: p for p in templates["playlists"]}
    out: dict[str, list[int]] = {}
    for profile in templates["profiles"]:
        playlist = by_slug[profile["playlist_slug"]]
        out[profile["investor_type"]] = [
            fund_risk[f["slug"] if isinstance(f, dict) else f]
            for f in playlist["funds"]
        ]
    return out


def test_every_profile_has_at_least_one_fund(templates, fund_risk) -> None:
    """An empty playlist means a user completes onboarding and sees nothing."""
    risks = _playlist_risks(templates, fund_risk)
    empty = [t for t, r in risks.items() if not r]
    assert not empty, f"Profiles with empty playlists: {empty}"


def test_mean_risk_is_monotonic_across_profiles(templates, fund_risk) -> None:
    """A more cautious profile must never be handed a riskier playlist."""
    risks = _playlist_risks(templates, fund_risk)
    means = [(t, mean(risks[t])) for t in RISK_ORDER if risks.get(t)]

    for (lower_type, lower), (higher_type, higher) in pairwise(means):
        assert lower <= higher, (
            f"{lower_type} playlist averages risk {lower:.2f} but the more "
            f"risk-tolerant {higher_type} averages {higher:.2f} — inverted."
        )


def test_conservative_holds_no_high_risk_funds(templates, fund_risk) -> None:
    """The cautious profile must not be sold the catalogue's riskiest products."""
    risks = _playlist_risks(templates, fund_risk)
    worst = max(risks["CONSERVATIVE"])
    assert worst <= 2, f"CONSERVATIVE playlist contains a risk-{worst} fund"
