from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class FeedSettings(BaseModel):
    """Platform-wide feed rules, editable in the admin.

    A single row, following InvestmentSettings: kept in the database rather
    than the environment so the window can be changed without a redeploy, and
    so the change is visible and attributable.
    """

    edit_window_minutes = models.PositiveIntegerField(
        default=60,
        help_text=(
            "How long after posting the author may still edit their own post, "
            "in minutes. Counted from when the post was created. Set to 0 to "
            "stop edits entirely — posts can always still be deleted, by the "
            "author or from this admin."
        ),
    )

    auto_hide_after_reports = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Hide a post automatically once this many different members have "
            "reported it, so a problem post stops being visible before a "
            "moderator gets to it. Hiding is reversible and the post is still "
            "listed here. Set to 0 to never hide automatically — sensible "
            "while the member base is small, since a handful of coordinated "
            "reports would otherwise be enough to silence anyone."
        ),
    )

    class Meta:
        db_table = "feed_settings"
        verbose_name = "Feed settings"
        verbose_name_plural = "Feed settings"

    def __str__(self) -> str:
        return f"Edit window: {self.edit_window_minutes} minutes"
