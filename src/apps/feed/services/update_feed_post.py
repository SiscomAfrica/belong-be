from __future__ import annotations

from uuid import UUID

from apps.feed.exceptions import FeedPostOwnershipError
from apps.feed.models import FeedPost
from apps.feed.selectors.get_feed_post import get_feed_post


def update_feed_post(
    *,
    post_id: UUID,
    user_id: UUID,
    user_comment: str | None = None,
    is_public: bool | None = None,
) -> FeedPost:
    post = get_feed_post(post_id=post_id)

    if post.user_id != user_id:
        raise FeedPostOwnershipError()

    update_fields: list[str] = []

    if user_comment is not None:
        post.user_comment = user_comment
        update_fields.append("user_comment")

    if is_public is not None:
        post.is_public = is_public
        update_fields.append("is_public")

    if update_fields:
        post.save(update_fields=[*update_fields, "updated_at"])

    return (
        FeedPost.objects.select_related("user", "investment__fund")
        .get(pk=post.pk)
    )
