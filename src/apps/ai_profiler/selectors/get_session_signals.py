from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.models import SessionQuestion
from apps.ai_profiler.services.score_vector import PRIMARY_WEIGHT, SECONDARY_WEIGHT


def get_session_signals(*, session_id: UUID) -> list[dict]:
    """Every behavioural reading taken so far in a session.

    Expands each answered question into one signal per anchor on each selected
    option. The question's wording is deliberately not carried through — only
    the anchors reach the scorer.
    """
    answered = (
        SessionQuestion.objects.filter(session_id=session_id, superseded_at=None)
        .exclude(answered_at=None)
        .order_by("position")
    )

    signals: list[dict] = []
    for question in answered:
        signals += signals_for_question(question=question)
    return signals


def signals_for_question(*, question: SessionQuestion) -> list[dict]:
    """Anchors from the options the user actually selected."""
    signals: list[dict] = []

    for index in question.selected_indexes:
        if index < 0 or index >= len(question.options):
            continue
        for anchor in question.options[index].get("anchors", []):
            behaviour = anchor.get("behaviour")
            signals.append({
                "behaviour": behaviour,
                "value": anchor.get("value"),
                "weight": (
                    PRIMARY_WEIGHT
                    if behaviour == question.primary_behaviour
                    else SECONDARY_WEIGHT
                ),
            })

    return signals
