from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class SessionStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    COMPLETED = "COMPLETED", "Completed"
    ABANDONED = "ABANDONED", "Abandoned"


class ConversationSession(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_sessions",
    )
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.ACTIVE,
        db_index=True,
    )
    summary = models.TextField(blank=True, default="")

    class Meta:
        db_table = "ai_profiler_session"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Session {self.id} [{self.status}]"
