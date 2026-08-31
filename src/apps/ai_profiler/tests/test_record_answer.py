from __future__ import annotations

import pytest

from apps.ai_profiler.selectors.get_session_signals import get_session_signals
from apps.ai_profiler.services.next_question import next_question
from apps.ai_profiler.services.record_answer import InvalidSelectionError, record_answer

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("no_llm")]


@pytest.fixture
def question(session):
    return next_question(session_id=session.id, user_id=session.user_id)


def test_re_answering_appends_rather_than_overwrites(question, session) -> None:
    """The question row is the audit record, so amendments must not erase it."""
    record_answer(
        question_id=question.id, user_id=session.user_id, selected_indexes=[0],
    )
    record_answer(
        question_id=question.id, user_id=session.user_id, selected_indexes=[1],
    )
    question.refresh_from_db()

    assert question.selected_indexes == [1]
    assert [r["selected_indexes"] for r in question.revisions] == [[0]]


def test_rejects_a_selection_outside_the_options(question, session) -> None:
    with pytest.raises(InvalidSelectionError, match="not among the options"):
        record_answer(
            question_id=question.id, user_id=session.user_id, selected_indexes=[99],
        )


def test_rejects_an_empty_selection(question, session) -> None:
    with pytest.raises(InvalidSelectionError, match="At least one option"):
        record_answer(
            question_id=question.id, user_id=session.user_id, selected_indexes=[],
        )


def test_rejects_a_repeated_selection(question, session) -> None:
    with pytest.raises(InvalidSelectionError, match="more than once"):
        record_answer(
            question_id=question.id, user_id=session.user_id, selected_indexes=[0, 0],
        )


def test_another_user_cannot_answer_your_question(question, other_user) -> None:
    with pytest.raises(Exception, match=r"[Ss]ession"):
        record_answer(
            question_id=question.id, user_id=other_user.id, selected_indexes=[0],
        )


def test_answering_produces_signals_without_question_wording(
    question, session, answer_first,
) -> None:
    """Only anchors reach the scorer — never the words the user was shown."""
    answer_first(question)
    signals = get_session_signals(session_id=session.id)

    assert signals
    assert all(set(signal) == {"behaviour", "value", "weight"} for signal in signals)


def test_unanswered_questions_produce_no_signals(question, session) -> None:
    assert get_session_signals(session_id=session.id) == []


def test_multi_select_records_every_choice(session, answer_first) -> None:
    question = next_question(session_id=session.id, user_id=session.user_id)
    record_answer(
        question_id=question.id, user_id=session.user_id, selected_indexes=[0, 1],
    )
    question.refresh_from_db()

    assert question.selected_indexes == [0, 1]
