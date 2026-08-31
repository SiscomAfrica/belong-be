from __future__ import annotations

import pytest

from apps.ai_profiler.services.validate_question import validate_question
from apps.ai_profiler.tests.question_factory import (
    anchor,
    option,
    question,
    risk_levels,
)


def test_anchors_spanning_2_to_4_are_acceptable() -> None:
    """2..4 reaches a cautious answer and a bold one, which is the actual bar."""
    assert validate_question(question=question(options=risk_levels("2", "3", "4"))) == []


@pytest.mark.parametrize(
    ("values", "reason"),
    [
        (("3", "4", "5"), "never offers a cautious answer"),
        (("1", "2", "3"), "never offers a bold answer"),
    ],
)
def test_rejects_anchors_that_miss_an_end(values: tuple, reason: str) -> None:
    """Three distinct integers always span three levels, so distinctness alone
    would let a question quietly compress every user toward the middle."""
    problems = validate_question(question=question(options=risk_levels(*values)))
    assert any("both ends of the scale" in p for p in problems), reason


def test_rejects_unclaimed_secondary_coverage() -> None:
    """Claiming a read you didn't take fakes coverage and skips a real question."""
    faked = question(
        secondary_behaviours=["mindset"],
        options=[
            option("A", anchor("risk", "1"), anchor("mindset", "3")),
            option("B", anchor("risk", "3"), anchor("mindset", "3")),
            option("C", anchor("risk", "5"), anchor("mindset", "3")),
        ],
    )
    assert any("claims to read mindset" in p for p in validate_question(question=faked))


def test_accepts_genuine_secondary_coverage() -> None:
    genuine = question(
        secondary_behaviours=["mindset"],
        options=[
            option("A", anchor("risk", "1"), anchor("mindset", "1")),
            option("B", anchor("risk", "3"), anchor("mindset", "3")),
            option("C", anchor("risk", "5"), anchor("mindset", "5")),
        ],
    )
    assert validate_question(question=genuine) == []


def test_categorical_primary_needs_three_distinct_values() -> None:
    thin = {
        "primary_behaviour": "market",
        "secondary_behaviours": [],
        "question": "Which of these sounds most like you?",
        "subtitle": "Go with your gut.",
        "options": [
            option("A", anchor("market", "TECH")),
            option("B", anchor("market", "GLOBAL")),
            option("C", anchor("market", "GLOBAL")),
        ],
    }
    assert validate_question(question=thin) != []
