from __future__ import annotations

from uuid import UUID

from apps.feed.exceptions import (
    FeedPostEditWindowClosedError,
    FeedPostOwnershipError,
)
from apps.feed.models import FeedPost
from apps.feed.selectors.get_edit_window import edit_cutoff, get_edit_window_minutes
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

    # Checked on the server, not merely hidden in the app: the window is the
    # rule, and a client that never refreshes would otherwise keep offering
    # an edit long after it lapsed.
    if post.created_at < edit_cutoff():
        raise FeedPostEditWindowClosedError(get_edit_window_minutes())

    update_fields: list[str] = []

    if user_comment is not None:
        post.user_comment = user_comment
        update_fields.append("user_comment")

    if is_public is not None:
        post.is_public = is_public
        update_fields.append("is_public")

    if update_fields:
        post.save(update_fields=[*update_fields, "updated_at"])

    fresh = (
        FeedPost.objects.select_related("user", "investment__fund")
        .get(pk=post.pk)
    )
    # Their own post, and it was editable a moment ago by definition.
    fresh.is_mine = True
    fresh.editable = True
    return fresh
