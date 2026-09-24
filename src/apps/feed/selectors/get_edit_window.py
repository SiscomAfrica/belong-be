from __future__ import annotations

import datetime as dt

from django.utils import timezone

from apps.feed.models import FeedSettings


def get_edit_window_minutes() -> int:
    """How long an author may still edit their post, in minutes.

    Reads the single admin-managed row, creating it with the field default if
    it is missing — a fresh database should not make posting fail, and the row
    then shows up in the admin ready to edit.
    """
    settings_row = FeedSettings.objects.first()
    if settings_row is None:
        settings_row = FeedSettings.objects.create()
    return settings_row.edit_window_minutes


def get_auto_hide_threshold() -> int:
    """How many distinct reports take a post out of the feed. 0 disables it."""
    settings_row = FeedSettings.objects.first()
    if settings_row is None:
        settings_row = FeedSettings.objects.create()
    return settings_row.auto_hide_after_reports


def edit_cutoff() -> dt.datetime:
    """Posts created before this moment can no longer be edited.

    Returned as a timestamp rather than a duration so callers can hand it
    straight to the database and decide editability for a whole page of posts
    in one query, instead of asking per post.
    """
    return timezone.now() - dt.timedelta(minutes=get_edit_window_minutes())
