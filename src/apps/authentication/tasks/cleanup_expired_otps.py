from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="apps.authentication.tasks.cleanup_expired_otps")
def cleanup_expired_otps() -> int:
    from apps.authentication.models import OTP

    deleted_count, _ = OTP.objects.filter(
        expires_at__lt=timezone.now(),
    ).delete()

    logger.info("Cleaned up %d expired OTPs", deleted_count)
    return deleted_count
