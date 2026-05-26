from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class MessageRole(models.TextChoices):
    SYSTEM = "SYSTEM", "System"
    USER = "USER", "User"
    ASSISTANT = "ASSISTANT", "Assistant"


class ConversationMessage(BaseModel):
    session = models.ForeignKey(
        "ai_profiler.ConversationSession",
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=MessageRole.choices)
    content = models.TextField()

    class Meta:
        db_table = "ai_profiler_message"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:50]}"
