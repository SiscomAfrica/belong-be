from __future__ import annotations

from uuid import UUID

from ninja import Router

from apps.ai_profiler.schemas import AnswerIn, NextQuestionOut, SessionQuestionOut
from apps.ai_profiler.selectors.get_session_questions import (
    display_position,
    previous_question,
)
from apps.ai_profiler.services.next_question import MAX_QUESTIONS, next_question
from apps.ai_profiler.services.record_answer import record_answer
from apps.ai_profiler.services.reopen_question import reopen_question

questions_router = Router(tags=["ai-profiler"])


@questions_router.post("/sessions/{session_id}/next-question", response=NextQuestionOut)
def next_question_endpoint(request, session_id: UUID):
    """Return the next question for a session, or signal that scoring can begin."""
    question = next_question(session_id=session_id, user_id=request.auth.id)
    if question is None:
        return NextQuestionOut(question=None, complete=True)
    return NextQuestionOut(question=present(question=question), complete=False)


@questions_router.post("/questions/{question_id}/answer", response=SessionQuestionOut)
def answer_question_endpoint(request, question_id: UUID, payload: AnswerIn):
    """Record the user's selection, or amend an earlier one."""
    question = record_answer(
        question_id=question_id,
        user_id=request.auth.id,
        selected_indexes=payload.selected_indexes,
    )
    return present(question=question)


@questions_router.post("/questions/{question_id}/previous", response=NextQuestionOut)
def previous_question_endpoint(request, question_id: UUID):
    """Step back to the question before this one, with its answer intact."""
    earlier = reopen_question(question_id=question_id, user_id=request.auth.id)
    if earlier is None:
        return NextQuestionOut(question=None, complete=False)
    return NextQuestionOut(question=present(question=earlier), complete=False)


def present(*, question) -> SessionQuestionOut:
    """Shape a stored question for the client. Anchors are never exposed."""
    position = display_position(question=question)

    return SessionQuestionOut(
        id=question.id,
        position=position,
        # Always the cap, never BASE_QUESTIONS.
        #
        # This used to report 4 until a fifth question existed and then switch
        # to 5, so the counter read "Question 4 of 4" and then "Question 5 of
        # 5" — the total moving under the user, which reads as the app having
        # changed its mind about how long this takes.
        #
        # With six behaviours and coverage needing one primary or two
        # secondary readings, the first four questions each only cover their
        # own primary; a fifth is always required. Announcing 5 and
        # occasionally finishing at 4 is a promise kept early, which is the
        # right way round.
        total_expected=MAX_QUESTIONS,
        prompt=question.prompt,
        subtitle=question.subtitle,
        allows_multiple=question.primary_behaviour == "motivation",
        selected_indexes=question.selected_indexes,
        has_previous=previous_question(question=question) is not None,
        options=[
            {"label": o.get("label", ""), "sublabel": o.get("sublabel", "")}
            for o in question.options
        ],
    )
