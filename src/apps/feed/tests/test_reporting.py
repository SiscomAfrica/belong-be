from __future__ import annotations

import pytest

from apps.common.exceptions import ValidationError
from apps.feed.models import FeedPost, FeedSettings, PostReport, ReportStatus
from apps.feed.selectors.list_feed_posts import list_feed_posts
from apps.feed.services.create_feed_post import create_feed_post
from apps.feed.services.report_post import report_post
from apps.users.models import User

pytestmark = pytest.mark.django_db


def member(n: int) -> User:
    return User.objects.create(
        phone=f"+2547000003{n:02d}", username=f"m{n}", referral_code=f"MEMBER{n:03d}",
    )


@pytest.fixture
def author() -> User:
    return member(1)


@pytest.fixture
def post(author: User) -> FeedPost:
    return create_feed_post(user_id=author.id, user_comment="Questionable claim")


def test_a_member_can_report_a_post(post: FeedPost) -> None:
    report = report_post(post_id=post.id, user_id=member(2).id, reason="MISLEADING")

    assert report.status == ReportStatus.PENDING
    assert report.reason == "MISLEADING"


def test_reporting_twice_is_a_no_op(post: FeedPost) -> None:
    """A second press is far more likely to be someone unsure it registered
    than a new complaint — and it must not let one account inflate the count.
    """
    reporter = member(3)

    first = report_post(post_id=post.id, user_id=reporter.id, reason="SPAM")
    second = report_post(post_id=post.id, user_id=reporter.id, reason="ABUSE")

    assert first.id == second.id
    assert PostReport.objects.filter(post=post).count() == 1


def test_you_cannot_report_your_own_post(post: FeedPost, author: User) -> None:
    with pytest.raises(ValidationError) as caught:
        report_post(post_id=post.id, user_id=author.id, reason="SPAM")

    assert caught.value.code == "FEED_POST_SELF_REPORT"


def test_an_unknown_reason_is_rejected(post: FeedPost) -> None:
    """Otherwise it lands in the admin filter as a category nobody can act on."""
    with pytest.raises(ValidationError):
        report_post(post_id=post.id, user_id=member(4).id, reason="BECAUSE")


def test_auto_hide_is_off_by_default(post: FeedPost) -> None:
    """A handful of coordinated reports should not be able to silence someone
    while the member base is small.
    """
    for n in (5, 6, 7):
        report_post(post_id=post.id, user_id=member(n).id, reason="SPAM")

    post.refresh_from_db()
    assert post.is_public


def test_auto_hide_pulls_a_post_once_enabled(post: FeedPost) -> None:
    FeedSettings.objects.all().delete()
    FeedSettings.objects.create(auto_hide_after_reports=2)

    report_post(post_id=post.id, user_id=member(8).id, reason="ABUSE")
    post.refresh_from_db()
    assert post.is_public

    report_post(post_id=post.id, user_id=member(9).id, reason="ABUSE")
    post.refresh_from_db()
    assert not post.is_public

    # And it leaves the feed, which is the point of hiding it.
    assert post.id not in {p.id for p in list_feed_posts(user_id=member(10).id)}
