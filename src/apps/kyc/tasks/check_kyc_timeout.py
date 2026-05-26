from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="apps.kyc.tasks.check_kyc_timeout")
def check_kyc_timeout() -> int:
    from apps.kyc.models import KYCStatus, KYCSubmission

    cutoff = timezone.now() - timedelta(hours=24)
    count = KYCSubmission.objects.filter(
        status=KYCStatus.PROCESSING,
        submitted_at__lt=cutoff,
    ).update(status=KYCStatus.MANUAL_REVIEW)
    logger.info("Moved %d KYC submissions to MANUAL_REVIEW", count)
    return count
