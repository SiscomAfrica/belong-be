from __future__ import annotations

from typing import ClassVar

from django.contrib import admin
from django.db.models import Count, Q, QuerySet

from apps.feed.admin_reports import PendingReportsFilter
from apps.feed.admin_settings import FeedSettingsAdmin  # noqa: F401
from apps.feed.models import FeedPost, PostReaction, ReportStatus


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    """Moderation for user-written posts.

    Everything here is public the moment it is written — there is no review
    queue — so this is where a post that should not have been shared is dealt
    with. Hiding is offered alongside deleting because it is reversible and
    keeps the evidence; deleting is for content that must not persist.
    """

    list_display = ("author", "body", "is_public", "reports", "likes_count", "created_at")
    list_filter = (PendingReportsFilter, "is_public", "created_at")
    search_fields = (
        "user_comment", "auto_text",
        "user__phone", "user__first_name", "user__last_name",
    )
    ordering = ("-created_at",)
    list_select_related = ("user", "investment__fund")
    actions: ClassVar[list[str]] = ["hide_posts", "unhide_posts"]
    readonly_fields = (
        "user", "investment", "auto_text", "likes_count",
        "created_at", "updated_at",
    )

    def get_queryset(self, request) -> QuerySet[FeedPost]:
        """Counts the pending reports in the same query as the page.

        Calling obj.reports.count() from the display method would be one
        query per row, which is exactly the shape that makes an admin list
        slow enough to stop being used.
        """
        return super().get_queryset(request).annotate(
            pending_reports=Count(
                "reports",
                filter=Q(reports__status=ReportStatus.PENDING),
                distinct=True,
            ),
        )

    @admin.display(description="Reports", ordering="pending_reports")
    def reports(self, obj: FeedPost) -> str:
        """Surfaced in the list so a flagged post is visible without opening
        the report queue separately."""
        return str(obj.pending_reports) if obj.pending_reports else "—"

    @admin.display(description="Author", ordering="user__phone")
    def author(self, obj: FeedPost) -> str:
        name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return f"{name} ({obj.user.phone})" if name else obj.user.phone

    @admin.display(description="Post")
    def body(self, obj: FeedPost) -> str:
        """What the moderator is actually deciding about.

        The list used to show only who and when, so judging a post meant
        opening it one at a time.
        """
        text = obj.user_comment or obj.auto_text or "—"
        return text if len(text) <= 90 else f"{text[:87]}…"

    @admin.action(description="Hide selected posts from the feed")
    def hide_posts(self, request, queryset) -> None:
        count = queryset.update(is_public=False)
        self.message_user(request, f"{count} post(s) hidden.")

    @admin.action(description="Show selected posts in the feed again")
    def unhide_posts(self, request, queryset) -> None:
        count = queryset.update(is_public=True)
        self.message_user(request, f"{count} post(s) restored.")


@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    ordering = ("-created_at",)

