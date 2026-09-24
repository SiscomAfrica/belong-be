from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone

from apps.kyc.models import KYCSubmission, KYCWebhookLog
from apps.kyc.providers.smile_identity import SmileIdentityProvider
from apps.kyc.services.apply_kyc_decision import apply_kyc_decision

logger = logging.getLogger(__name__)


def process_kyc_webhook(*, payload: dict) -> None:
    provider = SmileIdentityProvider()
    result = provider.verify_callback(payload=payload)

    log = KYCWebhookLog.objects.create(raw_payload=payload, result_code=result.result_code)

    if not result.job_id:
        logger.warning("KYC webhook missing job_id")
        return

    with transaction.atomic():
        try:
            submission = KYCSubmission.objects.select_for_update().get(
                smile_job_id=result.job_id,
            )
        except KYCSubmission.DoesNotExist:
            logger.warning("KYC submission not found for job_id=%s", result.job_id)
            return

        log.submission = submission
        log.processed_at = timezone.now()
        log.save()

        apply_kyc_decision(
            submission=submission,
            verified=result.success,
            result_text=result.result_text,
        )
