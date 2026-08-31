from __future__ import annotations

from uuid import UUID

from django.db.models import Max

from apps.ai_profiler.models import SessionQuestion


def active_questions(*, session_id: UUID) -> list[SessionQuestion]:
    """Questions still standing, oldest first. Superseded ones are excluded."""
    return list(
        SessionQuestion.objects.filter(session_id=session_id, superseded_at=None)
        .order_by("position"),
    )


def next_position(*, session_id: UUID) -> int:
    """The next storage position.

    Positions never repeat, including over superseded rows — reusing one would
    collide with the uniqueness constraint that keeps the audit trail ordered.
    The number the user sees is derived separately, in `display_position`.
    """
    highest = SessionQuestion.objects.filter(session_id=session_id).aggregate(
        highest=Max("position"),
    )["highest"]
    return (highest or 0) + 1


def display_position(*, question: SessionQuestion) -> int:
    """Where this question sits in the sequence the user is actually walking."""
    active = active_questions(session_id=question.session_id)
    for index, candidate in enumerate(active, start=1):
        if candidate.id == question.id:
            return index
    return len(active) + 1


def previous_question(*, question: SessionQuestion) -> SessionQuestion | None:
    """The question shown before this one, if any."""
    active = active_questions(session_id=question.session_id)
    for index, candidate in enumerate(active):
        if candidate.id == question.id:
            return active[index - 1] if index > 0 else None
    return None
