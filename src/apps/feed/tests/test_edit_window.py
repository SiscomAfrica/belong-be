from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.common.exceptions import ValidationError
from apps.feed.models import FeedPost, FeedSettings
from apps.feed.selectors.list_feed_posts import list_feed_posts
from apps.feed.services.create_feed_post import create_feed_post
from apps.feed.services.delete_feed_post import delete_feed_post
from apps.feed.services.update_feed_post import update_feed_post
from apps.users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def author() -> User:
    return User.objects.create(
        phone="+254700000021", username="fa", referral_code="FEEDAUTH1",
    )


@pytest.fixture
def reader() -> User:
    return User.objects.create(
        phone="+254700000022", username="fr", referral_code="FEEDREAD1",
    )


def aged(post: FeedPost, *, minutes: int) -> FeedPost:
    """Backdate a post. created_at is auto_now_add, so it needs an update()."""
    FeedPost.objects.filter(pk=post.pk).update(
        created_at=timezone.now() - timedelta(minutes=minutes),
    )
    return FeedPost.objects.get(pk=post.pk)


def test_a_fresh_post_can_be_edited(author: User) -> None:
    post = create_feed_post(user_id=author.id, user_comment="First go")

    updated = update_feed_post(
        post_id=post.id, user_id=author.id, user_comment="Second go",
    )

    assert updated.user_comment == "Second go"


def test_an_old_post_cannot(author: User) -> None:
    """The window is the rule, enforced here rather than only hidden in the app."""
    post = create_feed_post(user_id=author.id, user_comment="Too late")
    aged(post, minutes=61)

    with pytest.raises(ValidationError) as caught:
        update_feed_post(post_id=post.id, user_id=author.id, user_comment="nope")

    assert caught.value.code == "FEED_POST_EDIT_WINDOW_CLOSED"


def test_the_window_comes_from_the_admin_row(author: User) -> None:
    """Changing it in the admin changes behaviour with no redeploy."""
    FeedSettings.objects.all().delete()
    FeedSettings.objects.create(edit_window_minutes=5)
    post = create_feed_post(user_id=author.id, user_comment="Short window")
    aged(post, minutes=10)

    with pytest.raises(ValidationError):
        update_feed_post(post_id=post.id, user_id=author.id, user_comment="nope")


def test_deleting_your_own_post_is_not_time_limited(author: User) -> None:
    """Regret does not expire. Editing is capped so history cannot be quietly
    rewritten; removing your own words is always allowed.
    """
    post = create_feed_post(user_id=author.id, user_comment="Old but mine")
    aged(post, minutes=60 * 24 * 7)

    delete_feed_post(post_id=post.id, user_id=author.id)

    assert not FeedPost.objects.filter(pk=post.id).exists()


def test_the_feed_says_who_owns_what(author: User, reader: User) -> None:
    """The app shows edit and delete off these flags, so they have to be right."""
    fresh = create_feed_post(user_id=author.id, user_comment="Mine, new")
    stale = create_feed_post(user_id=author.id, user_comment="Mine, old")
    aged(stale, minutes=61)

    by_author = {p.id: p for p in list_feed_posts(user_id=author.id)}
    by_reader = {p.id: p for p in list_feed_posts(user_id=reader.id)}

    assert by_author[fresh.id].is_mine
    assert by_author[fresh.id].editable
    assert by_author[stale.id].is_mine
    assert not by_author[stale.id].editable
    assert not by_reader[fresh.id].is_mine
    assert not by_reader[fresh.id].editable


def test_a_hidden_post_leaves_the_feed(author: User, reader: User) -> None:
    """What the admin's Hide action does, from the reader's side."""
    post = create_feed_post(user_id=author.id, user_comment="Regrettable")
    FeedPost.objects.filter(pk=post.pk).update(is_public=False)

    assert post.id not in {p.id for p in list_feed_posts(user_id=reader.id)}
