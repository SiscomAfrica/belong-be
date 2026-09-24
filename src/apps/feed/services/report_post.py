from __future__ import annotations

from uuid import UUID

from django.db import IntegrityError, transaction

from apps.common.validation import sanitise_text, validate_choice
from apps.feed.exceptions import FeedPostSelfReportError
from apps.feed.models import FeedPost, PostReport, ReportReason, ReportStatus
from apps.feed.selectors.get_edit_window import get_auto_hide_threshold
from apps.feed.selectors.get_feed_post import get_feed_post


def report_post(
    *, post_id: UUID, user_id: UUID, reason: str, detail: str = "",
) -> PostReport:
    """Flag a post for moderation.

    Idempotent per member: reporting the same post twice returns the original
    report rather than failing. A second press of the button is far more
    likely to be someone unsure it registered than a genuinely new complaint,
    and an error there teaches people the feature is broken.
    """
    # The reason arrives as a free string, so it is checked against the
    # choices rather than stored as given — an unrecognised value would sit
    # in the admin filter as a category nobody can act on.
    reason = validate_choice(value=reason, allowed=ReportReason, field="reason")
    detail = sanitise_text(value=detail or "", field="detail", max_length=500)

    post = get_feed_post(post_id=post_id)

    if post.user_id == user_id:
        raise FeedPostSelfReportError()

    try:
        with transaction.atomic():
            report = PostReport.objects.create(
                post=post, reporter_id=user_id, reason=reason, detail=detail,
            )
    except IntegrityError:
        return PostReport.objects.get(post=post, reporter_id=user_id)

    _auto_hide_if_needed(post=post)
    return report


def _auto_hide_if_needed(*, post: FeedPost) -> None:
    """Take a post out of the feed once enough people have flagged it.

    Off by default. Hiding is reversible and the post stays in the admin, so
    the cost of acting early is low and the cost of leaving it up is not.
    """
    threshold = get_auto_hide_threshold()
    if threshold <= 0 or not post.is_public:
        return

    reports = PostReport.objects.filter(
        post=post, status=ReportStatus.PENDING,
    ).count()
    if reports >= threshold:
        FeedPost.objects.filter(pk=post.pk).update(is_public=False)
