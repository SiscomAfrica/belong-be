from __future__ import annotations

import pytest

from apps.ai_profiler.rubric import CENTROIDS
from apps.ai_profiler.services.match_profile import match_profile, weighted_distance

PROFILES = [
    {"investor_type": key, "centroid": centroid}
    for key, centroid in CENTROIDS.items()
]


def match(vector: dict) -> str:
    return match_profile(vector=vector, profiles=PROFILES)["investor_type"]


# Golden vectors. These are the contract: any change that moves one of these
# is a deliberate retune, not an accident, and should fail review loudly.
GOLDEN = [
    ({"risk": 1, "horizon": 1, "involvement": 1, "mindset": 1}, "CONSERVATIVE"),
    ({"risk": 2, "horizon": 3, "involvement": 2, "mindset": 3}, "MODERATE"),
    ({"risk": 3, "horizon": 4, "involvement": 3, "mindset": 3}, "INTERMEDIATE"),
    ({"risk": 4, "horizon": 4, "involvement": 3, "mindset": 4}, "AGGRESSIVE"),
    ({"risk": 5, "horizon": 5, "involvement": 4, "mindset": 5}, "HIGH_RISK"),
]


@pytest.mark.parametrize(("vector", "expected"), GOLDEN)
def test_golden_vectors(vector: dict, expected: str) -> None:
    assert match(vector) == expected


def test_every_profile_is_reachable() -> None:
    """The old keyword scorer could never produce HIGH_RISK. This one can."""
    reached = {match(vector) for vector, _ in GOLDEN}
    assert reached == set(CENTROIDS)


def test_ties_resolve_toward_lower_risk() -> None:
    """Ambiguity must never round a cautious user up into a riskier profile."""
    flat = {"horizon": 3, "involvement": 3, "mindset": 3}
    equidistant = [
        {"investor_type": "HIGH_RISK", "centroid": {"risk": 5, **flat}},
        {"investor_type": "CONSERVATIVE", "centroid": {"risk": 1, **flat}},
    ]
    vector = {"risk": 3, "horizon": 3, "involvement": 3, "mindset": 3}
    result = match_profile(vector=vector, profiles=equidistant)
    assert result["investor_type"] == "CONSERVATIVE"


def test_missing_behaviour_is_treated_as_median() -> None:
    partial = {"risk": 3, "horizon": None, "involvement": None, "mindset": None}
    full = {"risk": 3, "horizon": 3, "involvement": 3, "mindset": 3}
    assert match(partial) == match(full)


def test_risk_outweighs_the_other_axes() -> None:
    """A cautious risk answer should not be overridden by softer signals."""
    vector = {"risk": 1, "horizon": 5, "involvement": 4, "mindset": 4}
    assert match(vector) in {"CONSERVATIVE", "MODERATE"}


def test_distance_is_zero_at_the_centroid() -> None:
    from apps.ai_profiler.rubric import WEIGHTS

    centroid = CENTROIDS["MODERATE"]
    assert weighted_distance(vector=centroid, centroid=centroid, weights=WEIGHTS) == 0.0


def test_empty_profile_table_is_an_error() -> None:
    with pytest.raises(ValueError, match="at least one profile"):
        match_profile(vector={"risk": 3}, profiles=[])
