from __future__ import annotations

from uuid import UUID

from ninja import Query, Router

from apps.notifications.schemas import (
    MarkAllReadOut,
    NotificationListOut,
    NotificationOut,
    PushTokenOut,
    PushTokenRegisterIn,
)
from apps.notifications.selectors import get_unread_count, list_user_notifications
from apps.notifications.services import (
    mark_all_notifications_read,
    mark_notification_read,
    register_push_token,
)

notifications_router = Router(tags=["notifications"])


@notifications_router.post("/push-token", response={201: PushTokenOut})
def register_token(request, payload: PushTokenRegisterIn):  # noqa: ANN001, ANN201
    """Register a push notification token for the current device."""
    token = register_push_token(
        user_id=request.auth.id,
        token=payload.token,
        platform=payload.platform,
    )
    return 201, token


@notifications_router.get("/", response=NotificationListOut)
def list_notifications(request, is_read: bool | None = Query(None)):  # noqa: ANN001, ANN201
    """List notifications for the authenticated user."""
    qs = list_user_notifications(user_id=request.auth.id, is_read=is_read)
    unread = get_unread_count(user_id=request.auth.id)
    return {"items": list(qs), "count": qs.count(), "unread_count": unread}


@notifications_router.patch("/{notification_id}/read", response=NotificationOut)
def mark_read(request, notification_id: UUID):  # noqa: ANN001, ANN201
    """Mark a single notification as read."""
    return mark_notification_read(notification_id=notification_id, user_id=request.auth.id)


@notifications_router.post("/mark-all-read", response=MarkAllReadOut)
def mark_all_read(request):  # noqa: ANN001, ANN201
    """Mark all unread notifications as read."""
    count = mark_all_notifications_read(user_id=request.auth.id)
    return {"marked_count": count}
