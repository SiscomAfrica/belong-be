from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="apps.notifications.tasks.send_push_notification",
    max_retries=3,
    default_retry_delay=10,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
)
def send_push_notification(self, notification_id: str) -> int:  # noqa: ANN001
    from apps.notifications.services.send_push import send_push
    from uuid import UUID

    sent = send_push(notification_id=UUID(notification_id))
    logger.info(
        "Push sent task_id=%s notification_id=%s sent=%d",
        self.request.id,
        notification_id,
        sent,
    )
    return sent
