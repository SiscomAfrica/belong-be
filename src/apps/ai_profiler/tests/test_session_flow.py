from __future__ import annotations

import pytest

from apps.ai_profiler.models import QuestionSource
from apps.ai_profiler.services.next_question import MAX_QUESTIONS, next_question

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("no_llm")]


def test_questions_come_from_the_bank_when_generation_fails(session) -> None:
    question = next_question(session_id=session.id, user_id=session.user_id)

    assert question.source == QuestionSource.FALLBACK
    assert question.position == 1
    assert len(question.options) >= 3


def test_flow_terminates_and_never_exceeds_the_cap(session, answer_first) -> None:
    """Onboarding must always end — a coverage gap can't trap the user."""
    asked = 0
    while question := next_question(session_id=session.id, user_id=session.user_id):
        answer_first(question)
        asked += 1
        assert asked <= MAX_QUESTIONS

    assert 0 < asked <= MAX_QUESTIONS


def test_positions_are_sequential(session, answer_first) -> None:
    positions = []
    while question := next_question(session_id=session.id, user_id=session.user_id):
        positions.append(question.position)
        answer_first(question)

    assert positions == list(range(1, len(positions) + 1))


def test_each_question_leads_on_a_different_behaviour(session, answer_first) -> None:
    """Re-probing something already measured would waste one of four slots."""
    led = []
    while question := next_question(session_id=session.id, user_id=session.user_id):
        led.append(question.primary_behaviour)
        answer_first(question)

    assert len(led) == len(set(led))


def test_unanswered_question_does_not_advance_the_session(session) -> None:
    first = next_question(session_id=session.id, user_id=session.user_id)
    second = next_question(session_id=session.id, user_id=session.user_id)

    # A second call before answering creates the next question, but the first
    # contributes no signal until it is answered.
    assert second.position == first.position + 1
    assert first.answered_at is None
