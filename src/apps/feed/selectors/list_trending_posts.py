from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from django.db.models import Exists, OuterRef, QuerySet
from django.utils import timezone

from apps.feed.models import FeedPost, PostReaction


def list_trending_posts(*, user_id: UUID) -> QuerySet[FeedPost]:
    seven_days_ago = timezone.now() - timedelta(days=7)

    return (
        FeedPost.objects.filter(
            is_public=True,
            created_at__gte=seven_days_ago,
        )
        .select_related("user", "investment__fund")
        .annotate(
            is_liked=Exists(
                PostReaction.objects.filter(
                    post=OuterRef("pk"),
                    user_id=user_id,
                )
            )
        )
        .order_by("-likes_count", "-created_at")
    )
