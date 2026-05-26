from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.notifications.models import Notification


def list_user_notifications(
    *,
    user_id: UUID,
    is_read: bool | None = None,
) -> QuerySet[Notification]:
    qs = Notification.objects.filter(user_id=user_id)

    if is_read is not None:
        qs = qs.filter(is_read=is_read)

    return qs
