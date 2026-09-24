from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from django.db.models import QuerySet
from django.utils import timezone

from apps.feed.models import FeedPost
from apps.feed.selectors.list_feed_posts import annotate_viewer


def list_trending_posts(*, user_id: UUID) -> QuerySet[FeedPost]:
    seven_days_ago = timezone.now() - timedelta(days=7)

    return annotate_viewer(
        FeedPost.objects.filter(
            is_public=True,
            created_at__gte=seven_days_ago,
        ).select_related("user", "investment__fund"),
        user_id=user_id,
    ).order_by("-likes_count", "-created_at")
