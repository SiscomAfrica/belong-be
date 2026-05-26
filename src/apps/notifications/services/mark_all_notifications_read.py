from __future__ import annotations

from uuid import UUID

from apps.notifications.models import Notification


def mark_all_notifications_read(*, user_id: UUID) -> int:
    return Notification.objects.filter(
        user_id=user_id,
        is_read=False,
    ).update(is_read=True)
