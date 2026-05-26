from __future__ import annotations

from uuid import UUID

from django.db.models import Exists, OuterRef, QuerySet

from apps.feed.models import FeedPost, PostReaction


def list_feed_posts(*, user_id: UUID) -> QuerySet[FeedPost]:
    return (
        FeedPost.objects.filter(is_public=True)
        .select_related("user", "investment__fund")
        .annotate(
            is_liked=Exists(
                PostReaction.objects.filter(
                    post=OuterRef("pk"),
                    user_id=user_id,
                )
            )
        )
    )
