from __future__ import annotations

from uuid import UUID

from apps.notifications.exceptions import NotificationNotFoundError
from apps.notifications.models import Notification


def mark_notification_read(
    *,
    notification_id: UUID,
    user_id: UUID,
) -> Notification:
    try:
        notification = Notification.objects.get(id=notification_id, user_id=user_id)
    except Notification.DoesNotExist:
        raise NotificationNotFoundError

    notification.is_read = True
    notification.save(update_fields=["is_read", "updated_at"])
    return notification
