from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class PostReaction(BaseModel):
    post = models.ForeignKey(
        "feed.FeedPost",
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_reactions",
    )

    class Meta:
        db_table = "feed_post_reaction"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"],
                name="unique_post_user_reaction",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} liked {self.post_id}"
