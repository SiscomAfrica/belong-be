from __future__ import annotations

from django.contrib import admin

from apps.feed.models import FeedPost, PostReaction


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    list_display = ("user", "is_public", "likes_count", "created_at")
    search_fields = ("auto_text", "user_comment")
    list_filter = ("is_public",)
    ordering = ("-created_at",)


@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    ordering = ("-created_at",)
