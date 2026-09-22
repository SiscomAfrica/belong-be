from __future__ import annotations

from apps.ai_profiler.rubric import BEHAVIOUR_KEYS
from apps.ai_profiler.services.assess_coverage import (
    assess_coverage,
    next_behaviour_to_probe,
)
from apps.ai_profiler.services.fallback_questions import fallback_questions
from apps.ai_profiler.services.next_question import BASE_QUESTIONS, MAX_QUESTIONS

BANKED = {q["primary_behaviour"]: q for q in fallback_questions()}


def signals_for(question: dict, option_index: int) -> list[dict]:
    """What record_answer stores for one selected option."""
    option = question["options"][min(option_index, len(question["options"]) - 1)]
    primary = question["primary_behaviour"]
    return [
        {
            "behaviour": anchor["behaviour"],
            "value": anchor["value"],
            "weight": 1.0 if anchor["behaviour"] == primary else 0.5,
        }
        for anchor in option["anchors"]
    ]


def walk(option_index: int) -> tuple[int, list[str]]:
    """Play a whole session, always choosing the same option. Returns the
    number of questions asked and any behaviour left unmeasured.
    """
    signals: list[dict] = []
    asked = 0

    while asked < MAX_QUESTIONS:
        target = next_behaviour_to_probe(signals=signals)
        if target is None or target not in BANKED:
            break
        asked += 1
        signals += signals_for(BANKED[target], option_index)

    coverage = assess_coverage(signals=signals)
    return asked, [key for key in BEHAVIOUR_KEYS if not coverage[key]]


def test_a_session_asks_five_questions_whatever_the_answers() -> None:
    """Six behaviours, and coverage needs one primary or two secondary
    readings. The first four questions each only cover their own primary —
    their secondaries reach one reading and need two — so a fifth is always
    required. This is why the counter must not promise four.
    """
    for option_index in range(4):
        asked, _ = walk(option_index)
        assert asked == MAX_QUESTIONS, (
            f"choosing option {option_index + 1} asked {asked}, expected {MAX_QUESTIONS}"
        )


def test_five_questions_leave_nothing_imputed() -> None:
    """An imputed behaviour is filled with the population median rather than
    measured, so it is a real loss of signal. The banked set should not need
    it.
    """
    for option_index in range(4):
        _, missing = walk(option_index)
        assert missing == [], f"option {option_index + 1} left {missing} unmeasured"


def test_the_cap_sits_above_the_base_set() -> None:
    """If these ever meet, the follow-up question that covers the sixth
    behaviour can never be asked.
    """
    assert BASE_QUESTIONS < MAX_QUESTIONS
