from __future__ import annotations

from uuid import UUID

from django.db import IntegrityError
from django.db.models import F

from apps.feed.models import FeedPost, PostReaction


def toggle_like(*, post_id: UUID, user_id: UUID) -> bool:
    try:
        PostReaction.objects.create(post_id=post_id, user_id=user_id)
    except IntegrityError:
        PostReaction.objects.filter(
            post_id=post_id, user_id=user_id
        ).delete()
        FeedPost.objects.filter(pk=post_id).update(
            likes_count=F("likes_count") - 1
        )
        return False

    FeedPost.objects.filter(pk=post_id).update(
        likes_count=F("likes_count") + 1
    )
    return True
