from __future__ import annotations

from uuid import UUID

from apps.feed.exceptions import FeedPostNotFoundError
from apps.feed.models import FeedPost


def get_feed_post(*, post_id: UUID) -> FeedPost:
    try:
        return (
            FeedPost.objects.select_related("user", "investment__fund")
            .get(pk=post_id)
        )
    except FeedPost.DoesNotExist:
        raise FeedPostNotFoundError()
