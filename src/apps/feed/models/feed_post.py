from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class FeedPost(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feed_posts",
    )
    investment = models.ForeignKey(
        "investments.Investment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feed_posts",
    )
    auto_text = models.CharField(max_length=280, blank=True, default="")
    user_comment = models.CharField(max_length=500, blank=True, default="")
    is_public = models.BooleanField(default=True, db_index=True)
    likes_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "feed_post"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "is_public"]),
        ]

    def __str__(self) -> str:
        return f"Post by {self.user_id} at {self.created_at}"
