from __future__ import annotations

from apps.ai_profiler.services.validate_question import validate_question
from apps.ai_profiler.tests.question_factory import anchor, option, question


def test_a_well_formed_question_passes() -> None:
    assert validate_question(question=question()) == []


def test_rejects_duplicate_anchors() -> None:
    duplicated = question(options=[
        option("A", anchor("risk", "2")),
        option("B", anchor("risk", "2")),
        option("C", anchor("risk", "5")),
    ])
    assert any("share the same" in p for p in validate_question(question=duplicated))


def test_rejects_option_missing_the_primary_anchor() -> None:
    incomplete = question(options=[
        option("A", anchor("risk", "1")),
        option("B", anchor("risk", "3")),
        option("C", anchor("mindset", "5")),
    ])
    problems = validate_question(question=incomplete)
    assert any("must carry a risk anchor" in p for p in problems)


def test_rejects_anchor_outside_the_scale() -> None:
    bad = question(options=[
        option("A", anchor("risk", "0")),
        option("B", anchor("risk", "3")),
        option("C", anchor("risk", "5")),
    ])
    assert any("not a risk anchor" in p for p in validate_question(question=bad))


def test_rejects_unknown_behaviour() -> None:
    bad = question(options=[
        option("A", anchor("vibes", "1")),
        option("B", anchor("risk", "3")),
        option("C", anchor("risk", "5")),
    ])
    assert any("unknown behaviour" in p for p in validate_question(question=bad))


def test_rejects_too_few_options() -> None:
    thin = question(options=[
        option("A", anchor("risk", "1")),
        option("B", anchor("risk", "5")),
    ])
    assert any("expected 3-4 options" in p for p in validate_question(question=thin))


def test_rejects_overlong_label() -> None:
    wordy = question(options=[
        option("x" * 61, anchor("risk", "1")),
        option("B", anchor("risk", "3")),
        option("C", anchor("risk", "5")),
    ])
    assert any("label exceeds" in p for p in validate_question(question=wordy))


def test_missing_primary_behaviour_is_fatal() -> None:
    assert validate_question(question={"options": []}) == ["missing primary_behaviour"]
