from __future__ import annotations

from uuid import UUID

from django.db.models import BooleanField, Case, Exists, OuterRef, Q, QuerySet, Value, When

from apps.feed.models import FeedPost, PostReaction
from apps.feed.selectors.get_edit_window import edit_cutoff


def annotate_viewer(qs: QuerySet[FeedPost], *, user_id: UUID) -> QuerySet[FeedPost]:
    """Attach the three things that depend on who is asking.

    Annotated rather than resolved per post: `can_edit` needs the cutoff and
    the author, and computing that in a serializer would mean a settings read
    and an ownership check for every row on the page.
    """
    cutoff = edit_cutoff()
    mine = Q(user_id=user_id)

    return qs.annotate(
        is_liked=Exists(
            PostReaction.objects.filter(post=OuterRef("pk"), user_id=user_id),
        ),
        is_mine=Case(
            When(mine, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
        editable=Case(
            When(mine & Q(created_at__gte=cutoff), then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
    )


def list_feed_posts(*, user_id: UUID) -> QuerySet[FeedPost]:
    return annotate_viewer(
        FeedPost.objects.filter(is_public=True).select_related(
            "user", "investment__fund",
        ),
        user_id=user_id,
    )
