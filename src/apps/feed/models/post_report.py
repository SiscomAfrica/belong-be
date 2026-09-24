from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class ReportReason(models.TextChoices):
    SPAM = "SPAM", "Spam or advertising"
    MISLEADING = "MISLEADING", "Misleading financial claim"
    ABUSE = "ABUSE", "Abusive or offensive"
    PRIVACY = "PRIVACY", "Shares someone's private information"
    OTHER = "OTHER", "Something else"


class ReportStatus(models.TextChoices):
    PENDING = "PENDING", "Awaiting review"
    ACTIONED = "ACTIONED", "Actioned"
    DISMISSED = "DISMISSED", "Dismissed"


class PostReport(BaseModel):
    """One member flagging one post.

    Reports are the only way a problem post reaches a moderator: posts are
    public the moment they are written, and nothing else prompts anyone to
    look. Kept as rows rather than a counter on the post so the reason, the
    reporter and the outcome all survive review.
    """

    post = models.ForeignKey(
        "feed.FeedPost",
        on_delete=models.CASCADE,
        related_name="reports",
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_reports",
    )
    reason = models.CharField(max_length=20, choices=ReportReason.choices)
    detail = models.CharField(max_length=500, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
        db_index=True,
    )

    class Meta:
        db_table = "feed_post_report"
        ordering = ["-created_at"]
        constraints = [
            # One per person per post: reporting twice is not a stronger
            # signal, and it would let one account inflate the count.
            models.UniqueConstraint(
                fields=["post", "reporter"],
                name="unique_post_reporter_report",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.reason} report on {self.post_id}"
