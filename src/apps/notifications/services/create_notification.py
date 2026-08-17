from __future__ import annotations

from uuid import UUID

from apps.notifications.models import Notification
from apps.notifications.tasks import send_push_notification


def create_notification(
    *,
    user_id: UUID,
    type: str,
    title: str,
    body: str,
    action_url: str = "",
    metadata: dict | None = None,
) -> Notification:
    notification = Notification.objects.create(
        user_id=user_id,
        type=type,
        title=title,
        body=body,
        action_url=action_url,
        metadata=metadata or {},
    )
    send_push_notification.delay(str(notification.id))
    return notification
