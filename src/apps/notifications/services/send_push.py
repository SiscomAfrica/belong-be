from __future__ import annotations

import logging
from uuid import UUID

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)

from apps.notifications.models import DevicePushToken, Notification

logger = logging.getLogger(__name__)


def send_push(*, notification_id: UUID) -> int:
    notification = Notification.objects.select_related("user").get(
        id=notification_id,
    )
    tokens = list(
        DevicePushToken.objects.filter(
            user_id=notification.user_id,
            is_active=True,
        ).values_list("token", flat=True),
    )
    if not tokens:
        logger.info("No active tokens for user %s", notification.user_id)
        return 0

    messages = [
        PushMessage(
            to=token,
            title=notification.title,
            body=notification.body,
            data={
                "notification_id": str(notification.id),
                "type": notification.type,
                "action_url": notification.action_url,
            },
            sound="default",
            channel_id="belong",
        )
        for token in tokens
    ]
    return _publish_messages(messages)


def _publish_messages(messages: list[PushMessage]) -> int:
    client = PushClient()
    sent = 0
    for message in messages:
        try:
            response = client.publish(message)
            response.validate_response()
            sent += 1
        except DeviceNotRegisteredError:
            _deactivate_token(message.to)
        except (PushServerError, PushTicketError):
            logger.exception("Push failed for token %s", message.to)
        except Exception:
            logger.exception("Unexpected push error for %s", message.to)
    return sent


def _deactivate_token(token: str) -> None:
    updated = DevicePushToken.objects.filter(token=token).update(
        is_active=False,
    )
    if updated:
        logger.info("Deactivated stale push token: %s", token[:20])
