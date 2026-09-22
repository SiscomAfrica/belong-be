from __future__ import annotations

import pytest

from apps.ai_profiler.rubric import BEHAVIOUR_KEYS, CATEGORICAL_KEYS, ORDINAL_KEYS
from apps.ai_profiler.services.fallback_questions import fallback_questions
from apps.ai_profiler.services.question_exemplar import style_exemplar
from apps.ai_profiler.services.question_prompt import build_generation_prompt


@pytest.mark.parametrize("behaviour", ORDINAL_KEYS)
def test_ordinal_anchors_are_tagged_by_number(behaviour: str) -> None:
    prompt = build_generation_prompt(behaviour=behaviour, asked=[])

    assert "the number whose definition it matches" in prompt
    assert "KEY in capitals" not in prompt


@pytest.mark.parametrize("behaviour", CATEGORICAL_KEYS)
def test_categorical_anchors_are_tagged_by_key(behaviour: str) -> None:
    """Telling the model to "tag it with the number" for a categorical
    behaviour invites values that check_anchors then rejects — the question is
    thrown away and the user waits for a retry that fails the same way.
    """
    prompt = build_generation_prompt(behaviour=behaviour, asked=[])

    assert "the KEY in capitals whose definition it matches" in prompt
    assert "tag it with the number" not in prompt


@pytest.mark.parametrize("behaviour", BEHAVIOUR_KEYS)
def test_exemplar_never_shows_the_behaviour_being_written(behaviour: str) -> None:
    """The exemplar teaches register. Showing the banked question for the very
    behaviour being generated invites the model to hand it straight back,
    which would quietly collapse variety to the banked set.
    """
    banked = {
        question["primary_behaviour"]: question["question"] for question in fallback_questions()
    }
    own = banked.get(behaviour)
    exemplar = style_exemplar(behaviour=behaviour)

    assert exemplar
    if own:
        assert own not in exemplar


@pytest.mark.parametrize("behaviour", BEHAVIOUR_KEYS)
def test_prompt_carries_the_voice_rules(behaviour: str) -> None:
    prompt = build_generation_prompt(behaviour=behaviour, asked=[])

    assert "How to write it:" in prompt
    assert "Which of the following best describes" in prompt  # named as banned
    assert "The subtitle is one short line" in prompt


def test_prior_answers_never_reach_the_prompt() -> None:
    """Questions must not adapt to what the user has already said, or two
    users with the same behaviour get measured on different ground.

    Sentinel values rather than realistic copy: a plausible-looking answer
    string can coincide with an option label in the banked exemplar, which
    fails the assertion without anything having leaked.
    """
    asked = [
        {
            "question": "QUESTION-SENTINEL-must-appear",
            "answer": "ANSWER-SENTINEL-must-not-appear",
            "selected_value": "VALUE-SENTINEL-must-not-appear",
            "score": 5,
        },
    ]

    prompt = build_generation_prompt(behaviour="risk", asked=asked)

    assert "QUESTION-SENTINEL-must-appear" in prompt
    assert "ANSWER-SENTINEL-must-not-appear" not in prompt
    assert "VALUE-SENTINEL-must-not-appear" not in prompt
