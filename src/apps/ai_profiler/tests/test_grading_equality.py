from __future__ import annotations

from random import Random

from apps.ai_profiler.rubric import CENTROIDS
from apps.ai_profiler.services.match_profile import match_profile
from apps.ai_profiler.services.score_vector import score_vector

PROFILES = [
    {"investor_type": key, "centroid": centroid}
    for key, centroid in CENTROIDS.items()
]


def grade(signals: list[dict]) -> str:
    vector = score_vector(signals=signals)
    return match_profile(vector=vector, profiles=PROFILES)["investor_type"]


# Two users, two entirely different question sets, identical behaviour.
# This is the property the whole design exists to provide.

CAUTIOUS_SESSION_A = [
    {"behaviour": "risk", "value": 1, "weight": 1.0},
    {"behaviour": "horizon", "value": 2, "weight": 1.0},
    {"behaviour": "involvement", "value": 1, "weight": 1.0},
    {"behaviour": "mindset", "value": 1, "weight": 0.5},
    {"behaviour": "mindset", "value": 1, "weight": 0.5},
    {"behaviour": "motivation", "value": "SECURITY", "weight": 1.0},
    {"behaviour": "market", "value": "DEFENSIVE", "weight": 0.5},
]

# Same anchors, different order, different primary/secondary split — i.e. the
# generator asked about these behaviours in a different shape.
CAUTIOUS_SESSION_B = [
    {"behaviour": "market", "value": "DEFENSIVE", "weight": 0.5},
    {"behaviour": "mindset", "value": 1, "weight": 1.0},
    {"behaviour": "motivation", "value": "SECURITY", "weight": 1.0},
    {"behaviour": "involvement", "value": 1, "weight": 1.0},
    {"behaviour": "horizon", "value": 2, "weight": 1.0},
    {"behaviour": "risk", "value": 1, "weight": 1.0},
]


def test_same_behaviour_different_questions_grades_identically() -> None:
    assert grade(CAUTIOUS_SESSION_A) == grade(CAUTIOUS_SESSION_B)


def test_signal_order_never_changes_the_result() -> None:
    """Question order is a presentation choice and must not move the outcome."""
    rng = Random(20260829)  # noqa: S311 — deterministic seed, not crypto
    baseline = grade(CAUTIOUS_SESSION_A)
    for _ in range(50):
        shuffled = CAUTIOUS_SESSION_A[:]
        rng.shuffle(shuffled)
        assert grade(shuffled) == baseline


def test_scoring_is_pure() -> None:
    """Repeated calls on the same input never drift."""
    first = score_vector(signals=CAUTIOUS_SESSION_A)
    for _ in range(10):
        assert score_vector(signals=CAUTIOUS_SESSION_A) == first


def test_input_is_not_mutated() -> None:
    before = [dict(signal) for signal in CAUTIOUS_SESSION_A]
    score_vector(signals=CAUTIOUS_SESSION_A)
    assert before == CAUTIOUS_SESSION_A
