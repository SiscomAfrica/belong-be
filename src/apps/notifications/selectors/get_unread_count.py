from __future__ import annotations

from uuid import UUID

from apps.notifications.models import Notification


def get_unread_count(*, user_id: UUID) -> int:
    return Notification.objects.filter(
        user_id=user_id,
        is_read=False,
    ).count()
