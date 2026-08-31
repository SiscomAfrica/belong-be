from __future__ import annotations

import pytest

from apps.ai_profiler.services.banned_copy import copy_problems
from apps.ai_profiler.services.fallback_questions import (
    fallback_for,
    fallback_questions,
)
from apps.ai_profiler.services.validate_question import validate_question

BANKED = fallback_questions()


@pytest.mark.parametrize("banked", BANKED, ids=lambda q: q["primary_behaviour"])
def test_every_banked_question_is_valid(banked: dict) -> None:
    """The fallback bank must clear the same bar as generated output.

    If it did not, a user who hit a generation failure would be graded by a
    question set that never passed review — which is the loophole this closes.
    """
    assert validate_question(question=banked) == []


def test_bank_covers_enough_behaviours_to_score() -> None:
    led = {question["primary_behaviour"] for question in BANKED}
    assert {"risk", "horizon"} <= led


def test_fallback_lookup_finds_by_behaviour() -> None:
    assert fallback_for(behaviour="risk")["primary_behaviour"] == "risk"
    assert fallback_for(behaviour="nonexistent") is None


def test_fallback_returns_a_copy() -> None:
    """Callers stamp `source` onto the result; the bank must not mutate."""
    first = fallback_for(behaviour="risk")
    first["question"] = "mutated"
    assert fallback_for(behaviour="risk")["question"] != "mutated"


@pytest.mark.parametrize(
    "text",
    [
        "Which risk-free option suits you?",
        "Want a guaranteed return on your money?",
        "Would you like to beat the market?",
        "Pick the top performing option",
        "This one can't lose",
    ],
)
def test_banned_phrases_are_caught(text: str) -> None:
    assert copy_problems(text=text)


@pytest.mark.parametrize(
    "text",
    ["A 130% gain", "up 12.5 %", "returns of -8%", "+63.89% last year"],
)
def test_return_figures_are_caught(text: str) -> None:
    assert any("return figure" in p for p in copy_problems(text=text))


@pytest.mark.parametrize(
    "text",
    [
        "How would a sharp drop sit with you?",
        "When do you expect to use this money?",
        "Which of these sounds most like you?",
    ],
)
def test_ordinary_copy_passes(text: str) -> None:
    assert copy_problems(text=text) == []


def test_non_compliant_copy_fails_the_whole_question() -> None:
    banked = fallback_for(behaviour="risk")
    banked["question"] = "Want a guaranteed return?"
    assert validate_question(question=banked) != []
