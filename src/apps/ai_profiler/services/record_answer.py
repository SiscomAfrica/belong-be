from __future__ import annotations

from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.ai_profiler.exceptions import SessionNotFoundError
from apps.ai_profiler.models import SessionQuestion


class InvalidSelectionError(ValueError):
    """Raised when a selection does not index into the options that were shown."""


def record_answer(
    *, question_id: UUID, user_id: UUID, selected_indexes: list[int],
) -> SessionQuestion:
    """Record which options the user chose, or amend an earlier choice.

    Amending never overwrites history: the previous selection is appended to
    `revisions`, so the record of what was asked and every answer given to it
    stays intact.

    Changing an answer can change which behaviours are covered, so every later
    question is superseded rather than left standing on a premise that no
    longer holds.
    """
    question = _owned_question(question_id=question_id, user_id=user_id)
    _validate(selected=selected_indexes, option_count=len(question.options))

    now = timezone.now()

    with transaction.atomic():
        if question.answered_at is not None:
            question.revisions = [
                *question.revisions,
                {
                    "selected_indexes": question.selected_indexes,
                    "answered_at": question.answered_at.isoformat(),
                },
            ]
            _supersede_after(question=question, at=now)

        question.selected_indexes = selected_indexes
        question.answered_at = now
        question.superseded_at = None
        question.save(update_fields=[
            "selected_indexes", "revisions", "answered_at", "superseded_at", "updated_at",
        ])

    return question


def _supersede_after(*, question: SessionQuestion, at) -> None:
    SessionQuestion.objects.filter(
        session_id=question.session_id,
        position__gt=question.position,
        superseded_at=None,
    ).update(superseded_at=at)


def _owned_question(*, question_id: UUID, user_id: UUID) -> SessionQuestion:
    try:
        return SessionQuestion.objects.select_related("session").get(
            id=question_id, session__user_id=user_id,
        )
    except SessionQuestion.DoesNotExist:
        raise SessionNotFoundError() from None


def _validate(*, selected: list[int], option_count: int) -> None:
    if not selected:
        msg = "At least one option must be selected"
        raise InvalidSelectionError(msg)

    if len(set(selected)) != len(selected):
        msg = "The same option was selected more than once"
        raise InvalidSelectionError(msg)

    out_of_range = [i for i in selected if i < 0 or i >= option_count]
    if out_of_range:
        msg = f"Selection {out_of_range} is not among the options shown"
        raise InvalidSelectionError(msg)
