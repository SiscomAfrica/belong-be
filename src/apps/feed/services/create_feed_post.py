from __future__ import annotations

from uuid import UUID

from apps.feed.models import FeedPost


def create_feed_post(
    *,
    user_id: UUID,
    investment_id: UUID | None = None,
    auto_text: str = "",
    user_comment: str = "",
    is_public: bool = True,
) -> FeedPost:
    post = FeedPost.objects.create(
        user_id=user_id,
        investment_id=investment_id,
        auto_text=auto_text,
        user_comment=user_comment,
        is_public=is_public,
    )
    return (
        FeedPost.objects.select_related("user", "investment__fund")
        .get(pk=post.pk)
    )
