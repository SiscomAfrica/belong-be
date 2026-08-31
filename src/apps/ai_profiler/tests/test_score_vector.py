from __future__ import annotations

import pytest

from apps.ai_profiler.rubric import BEHAVIOUR_KEYS
from apps.ai_profiler.services.assess_coverage import (
    assess_coverage,
    next_behaviour_to_probe,
    uncovered_behaviours,
)
from apps.ai_profiler.services.score_vector import score_vector


def test_vector_always_has_all_six_slots() -> None:
    vector = score_vector(signals=[])
    assert set(vector) == set(BEHAVIOUR_KEYS)
    assert all(value is None for value in vector.values())


def test_ordinal_resolves_to_weighted_mean() -> None:
    signals = [
        {"behaviour": "risk", "value": 4, "weight": 1.0},
        {"behaviour": "risk", "value": 2, "weight": 1.0},
    ]
    assert score_vector(signals=signals)["risk"] == 3


def test_primary_signal_outweighs_secondary() -> None:
    signals = [
        {"behaviour": "risk", "value": 5, "weight": 1.0},
        {"behaviour": "risk", "value": 1, "weight": 0.5},
    ]
    # (5*1.0 + 1*0.5) / 1.5 = 3.67 -> 4
    assert score_vector(signals=signals)["risk"] == 4


@pytest.mark.parametrize("level", [-3, 0, 9, 99])
def test_ordinal_is_clamped_to_the_scale(level: int) -> None:
    signals = [{"behaviour": "risk", "value": level, "weight": 1.0}]
    assert 1 <= score_vector(signals=signals)["risk"] <= 5


def test_categorical_picks_highest_weight() -> None:
    signals = [
        {"behaviour": "market", "value": "TECH", "weight": 0.5},
        {"behaviour": "market", "value": "GLOBAL", "weight": 1.0},
    ]
    assert score_vector(signals=signals)["market"] == "GLOBAL"


def test_categorical_tie_breaks_on_first_appearance() -> None:
    signals = [
        {"behaviour": "market", "value": "TECH", "weight": 1.0},
        {"behaviour": "market", "value": "GLOBAL", "weight": 1.0},
    ]
    assert score_vector(signals=signals)["market"] == "TECH"


def test_unknown_behaviours_are_ignored() -> None:
    signals = [{"behaviour": "vibes", "value": 4, "weight": 1.0}]
    assert all(value is None for value in score_vector(signals=signals).values())


def test_one_primary_signal_covers_a_behaviour() -> None:
    signals = [{"behaviour": "risk", "value": 3, "weight": 1.0}]
    assert assess_coverage(signals=signals)["risk"] is True


def test_one_secondary_signal_is_not_enough() -> None:
    signals = [{"behaviour": "risk", "value": 3, "weight": 0.5}]
    assert assess_coverage(signals=signals)["risk"] is False


def test_two_secondary_signals_cover_a_behaviour() -> None:
    signals = [
        {"behaviour": "risk", "value": 3, "weight": 0.5},
        {"behaviour": "risk", "value": 4, "weight": 0.5},
    ]
    assert assess_coverage(signals=signals)["risk"] is True


def test_probe_targets_the_first_uncovered_behaviour() -> None:
    signals = [{"behaviour": "motivation", "value": "WEALTH", "weight": 1.0}]
    assert next_behaviour_to_probe(signals=signals) == "risk"
    assert "motivation" not in uncovered_behaviours(signals=signals)


def test_no_probe_needed_once_everything_is_covered() -> None:
    signals = [
        {"behaviour": key, "value": 3 if key not in ("motivation", "market") else "WEALTH",
         "weight": 1.0}
        for key in BEHAVIOUR_KEYS
    ]
    assert next_behaviour_to_probe(signals=signals) is None
