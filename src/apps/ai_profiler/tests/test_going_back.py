from __future__ import annotations

import pytest

from apps.ai_profiler.models import SessionQuestion
from apps.ai_profiler.selectors.get_session_questions import (
    active_questions,
    display_position,
)
from apps.ai_profiler.selectors.get_session_signals import get_session_signals
from apps.ai_profiler.services.next_question import next_question
from apps.ai_profiler.services.record_answer import record_answer
from apps.ai_profiler.services.reopen_question import reopen_question

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("no_llm")]


@pytest.fixture
def two_questions(session, answer_first):
    first = next_question(session_id=session.id, user_id=session.user_id)
    answer_first(first)
    first.refresh_from_db()
    second = next_question(session_id=session.id, user_id=session.user_id)
    return first, second


def test_first_question_has_nowhere_to_go_back_to(session) -> None:
    first = next_question(session_id=session.id, user_id=session.user_id)
    assert reopen_question(question_id=first.id, user_id=session.user_id) is None


def test_going_back_returns_the_same_question_not_a_new_one(two_questions, session) -> None:
    """Regenerating on Back would swap the question out from under the user."""
    first, second = two_questions
    earlier = reopen_question(question_id=second.id, user_id=session.user_id)

    assert earlier.id == first.id
    assert earlier.prompt == first.prompt
    assert earlier.options == first.options


def test_reopened_question_still_carries_its_answer(two_questions, session) -> None:
    first, second = two_questions
    earlier = reopen_question(question_id=second.id, user_id=session.user_id)
    assert earlier.selected_indexes == first.selected_indexes


def test_amending_preserves_the_original_answer(two_questions, session) -> None:
    """Write-once meant never destroying the record, not never amending it."""
    first, _ = two_questions
    original = list(first.selected_indexes)

    record_answer(question_id=first.id, user_id=session.user_id, selected_indexes=[1])
    first.refresh_from_db()

    assert first.selected_indexes == [1]
    assert len(first.revisions) == 1
    assert first.revisions[0]["selected_indexes"] == original


def test_amending_supersedes_later_questions(two_questions, session) -> None:
    """A changed answer can change coverage, so what followed it is unsound."""
    first, second = two_questions

    record_answer(question_id=first.id, user_id=session.user_id, selected_indexes=[1])
    second.refresh_from_db()

    assert second.superseded_at is not None
    assert [q.id for q in active_questions(session_id=session.id)] == [first.id]


def test_superseded_questions_contribute_no_signals(two_questions, session, answer_first) -> None:
    first, second = two_questions
    answer_first(second)
    before = len(get_session_signals(session_id=session.id))

    record_answer(question_id=first.id, user_id=session.user_id, selected_indexes=[1])
    after = get_session_signals(session_id=session.id)

    assert len(after) < before


def test_positions_are_never_reused(two_questions, session) -> None:
    """Reusing a superseded position would collide with the ordering constraint."""
    first, _ = two_questions
    record_answer(question_id=first.id, user_id=session.user_id, selected_indexes=[1])

    replacement = next_question(session_id=session.id, user_id=session.user_id)
    stored = SessionQuestion.objects.filter(session_id=session.id).count()

    assert replacement.position == 3
    assert stored == 3
    assert display_position(question=replacement) == 2
