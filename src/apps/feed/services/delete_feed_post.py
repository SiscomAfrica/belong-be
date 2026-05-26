from __future__ import annotations

from uuid import UUID

from apps.feed.exceptions import FeedPostOwnershipError
from apps.feed.selectors.get_feed_post import get_feed_post


def delete_feed_post(*, post_id: UUID, user_id: UUID) -> None:
    post = get_feed_post(post_id=post_id)

    if post.user_id != user_id:
        raise FeedPostOwnershipError()

    post.delete()
