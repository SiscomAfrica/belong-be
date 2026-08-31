from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class QuestionSource(models.TextChoices):
    GENERATED = "GENERATED", "Generated"
    FALLBACK = "FALLBACK", "Fallback"


class SessionQuestion(BaseModel):
    """One question as it was actually put to one user, with their answer.

    Generated questions are not reproducible after the fact — asking the model
    again yields different wording. If a regulator asks why a user landed in a
    profile, this row is the only record of what they were actually shown, so
    it is written once and never updated in place.
    """

    session = models.ForeignKey(
        "ai_profiler.ConversationSession",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    position = models.PositiveSmallIntegerField(
        help_text="1-indexed order the question was asked in",
    )
    primary_behaviour = models.CharField(max_length=20, db_index=True)
    secondary_behaviours = models.JSONField(default=list)
    source = models.CharField(
        max_length=10,
        choices=QuestionSource.choices,
        default=QuestionSource.GENERATED,
    )
    prompt = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, default="")
    options = models.JSONField(
        default=list,
        help_text="Options exactly as shown, each with its anchor tags",
    )
    selected_indexes = models.JSONField(
        default=list,
        help_text="Indexes into `options` that the user chose",
    )
    revisions = models.JSONField(
        default=list,
        blank=True,
        help_text="Prior selections, appended when the user goes back and amends",
    )
    answered_at = models.DateTimeField(null=True, blank=True)
    superseded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set when an earlier answer changed and made this question unsound",
    )

    class Meta:
        db_table = "ai_profiler_session_question"
        ordering = ["session", "position"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "position"],
                name="unique_session_question_position",
            ),
        ]

    def __str__(self) -> str:
        return f"Q{self.position} [{self.primary_behaviour}] of {self.session_id}"
