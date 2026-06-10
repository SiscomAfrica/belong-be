from __future__ import annotations

from uuid import UUID

from ninja import Router

from apps.feed.schemas import (
    FeedListOut,
    FeedPostCreateIn,
    FeedPostOut,
    FeedPostUpdateIn,
    LikeToggleOut,
)
from apps.feed.selectors import (
    list_feed_posts,
    list_trending_posts,
)
from apps.feed.services import (
    create_feed_post,
    delete_feed_post,
    toggle_like,
    update_feed_post,
)

feed_router = Router(tags=["feed"])


@feed_router.post("/posts", response={201: FeedPostOut})
def create(request, payload: FeedPostCreateIn):  # noqa: ANN001, ANN201
    """Create a new social feed post, optionally linked to an investment."""
    post = create_feed_post(
        user_id=request.auth.id,
        investment_id=payload.investment_id,
        auto_text=payload.auto_text,
        user_comment=payload.user_comment,
        is_public=payload.is_public,
    )
    return 201, post


@feed_router.get("/", response=FeedListOut)
def list_posts(request):  # noqa: ANN001, ANN201
    """List feed posts visible to the authenticated user."""
    qs = list_feed_posts(user_id=request.auth.id)
    return {"items": list(qs), "count": qs.count()}


@feed_router.get("/trending", response=FeedListOut)
def trending(request):  # noqa: ANN001, ANN201
    """List trending feed posts ranked by engagement."""
    qs = list_trending_posts(user_id=request.auth.id)
    return {"items": list(qs), "count": qs.count()}


@feed_router.post("/posts/{post_id}/like", response=LikeToggleOut)
def like(request, post_id: UUID):  # noqa: ANN001, ANN201
    """Toggle like on a feed post. Returns current liked state."""
    liked = toggle_like(post_id=post_id, user_id=request.auth.id)
    return {"liked": liked}


@feed_router.patch("/posts/{post_id}", response=FeedPostOut)
def update(request, post_id: UUID, payload: FeedPostUpdateIn):  # noqa: ANN001, ANN201
    """Update comment or visibility of an existing feed post."""
    return update_feed_post(
        post_id=post_id,
        user_id=request.auth.id,
        user_comment=payload.user_comment,
        is_public=payload.is_public,
    )


@feed_router.delete("/posts/{post_id}", response={204: None})
def delete(request, post_id: UUID):  # noqa: ANN001, ANN201
    """Delete a feed post owned by the authenticated user."""
    delete_feed_post(post_id=post_id, user_id=request.auth.id)
    return 204, None
