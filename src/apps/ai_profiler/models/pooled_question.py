from __future__ import annotations

from django.db import models

from apps.ai_profiler.models.session_question import QuestionSource
from apps.common.models.base import BaseModel


class PooledQuestion(BaseModel):
    """A generated question waiting to be handed to the next session that needs it.

    Generation is an LLM round-trip — seconds, not milliseconds — and it used
    to sit directly on the path between tapping Continue and seeing the next
    question. Nothing about a question depends on *who* is answering it: the
    prompt is built from the behaviour and the rubric alone, never from the
    user or their prior answers (deliberately, so two users are graded on the
    same ground). That is what makes it safe to build them ahead of time.

    A row is claimed exactly once. Claiming deletes nothing — `claimed_at` is
    set instead, so a question that turned out badly can still be traced back
    from the session that served it.
    """

    behaviour = models.CharField(max_length=32, db_index=True)
    prompt = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=200, blank=True, default="")
    options = models.JSONField(default=list)
    secondary_behaviours = models.JSONField(default=list)
    source = models.CharField(
        max_length=20,
        choices=QuestionSource.choices,
        default=QuestionSource.GENERATED,
    )
    claimed_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "ai_profiler_pooled_question"
        ordering = ["created_at"]
        indexes = [
            # The only hot query: the oldest unclaimed row for one behaviour.
            models.Index(
                fields=["behaviour", "claimed_at", "created_at"],
                name="pooled_q_available_idx",
            ),
        ]

    def __str__(self) -> str:
        state = "claimed" if self.claimed_at else "available"
        return f"{self.behaviour} ({state})"
