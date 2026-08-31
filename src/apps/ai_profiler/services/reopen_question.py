from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.exceptions import SessionNotFoundError
from apps.ai_profiler.models import SessionQuestion
from apps.ai_profiler.selectors.get_session_questions import previous_question


def reopen_question(*, question_id: UUID, user_id: UUID) -> SessionQuestion | None:
    """Step back to the question before `question_id`, or None if it is the first.

    Nothing is regenerated. The stored question is re-served exactly as it was
    shown, along with the answer already given, so going back never quietly
    swaps the question out from under the user.
    """
    try:
        current = SessionQuestion.objects.select_related("session").get(
            id=question_id, session__user_id=user_id,
        )
    except SessionQuestion.DoesNotExist:
        raise SessionNotFoundError() from None

    return previous_question(question=current)
