from __future__ import annotations

from typing import ClassVar

from django.contrib import admin

from apps.feed.models import FeedPost, PostReport, ReportStatus


class PendingReportsFilter(admin.SimpleListFilter):
    """Answers the only question a moderator opens this page to ask."""

    title = "pending reports"
    parameter_name = "pending"

    def lookups(self, request, model_admin):
        return (("yes", "Has pending reports"), ("no", "None pending"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(reports__status=ReportStatus.PENDING).distinct()
        if self.value() == "no":
            return queryset.exclude(reports__status=ReportStatus.PENDING)
        return queryset


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    """The moderation queue.

    Posts go live unreviewed, so this is the only thing that surfaces one that
    should not have. Sorted newest first and filtered by status, because the
    question is almost always "what has come in that nobody has looked at".
    """

    list_display = ("created_at", "reason", "status", "reported_post", "reporter_name")
    list_filter = ("status", "reason", "created_at")
    search_fields = (
        "detail", "post__user_comment", "post__auto_text",
        "reporter__phone", "post__user__phone",
    )
    ordering = ("-created_at",)
    list_select_related = ("post__user", "reporter")
    actions: ClassVar[list[str]] = ["hide_and_action", "dismiss"]
    readonly_fields = ("post", "reporter", "reason", "detail", "created_at", "updated_at")

    @admin.display(description="Post")
    def reported_post(self, obj: PostReport) -> str:
        text = obj.post.user_comment or obj.post.auto_text or "—"
        shown = text if len(text) <= 70 else f"{text[:67]}…"
        return f"{shown} {'(hidden)' if not obj.post.is_public else ''}".strip()

    @admin.display(description="Reported by")
    def reporter_name(self, obj: PostReport) -> str:
        return obj.reporter.phone

    @admin.action(description="Hide the post and mark reports actioned")
    def hide_and_action(self, request, queryset) -> None:
        post_ids = list(queryset.values_list("post_id", flat=True))
        FeedPost.objects.filter(pk__in=post_ids).update(is_public=False)
        count = queryset.update(status=ReportStatus.ACTIONED)
        self.message_user(request, f"{count} report(s) actioned; post(s) hidden.")

    @admin.action(description="Dismiss — the post is fine")
    def dismiss(self, request, queryset) -> None:
        count = queryset.update(status=ReportStatus.DISMISSED)
        self.message_user(request, f"{count} report(s) dismissed.")
