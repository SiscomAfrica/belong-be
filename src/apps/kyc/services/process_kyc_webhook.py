from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.kyc.models import KYCStatus, KYCSubmission, KYCWebhookLog
from apps.kyc.providers.smile_identity import SmileIdentityProvider
from apps.notifications.services.create_notification import create_notification

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

        new_status = KYCStatus.VERIFIED if result.success else KYCStatus.REJECTED
        submission.status = new_status
        submission.result_text = result.result_text
        submission.save()

        audit_action = AuditAction.KYC_APPROVED if result.success else AuditAction.KYC_REJECTED
        create_audit_log(
            action=audit_action,
            entity_type="KYCSubmission",
            entity_id=submission.id,
            actor_id=submission.user_id,
            new_values={"status": new_status, "result_code": result.result_code},
        )
        notif_type = "KYC_APPROVED" if result.success else "KYC_REJECTED"
        title = "KYC Verified" if result.success else "KYC Rejected"
        body = (
            "Your identity has been verified successfully."
            if result.success
            else f"Your KYC was rejected: {result.result_text}"
        )
        create_notification(
            user_id=submission.user_id, type=notif_type, title=title, body=body,
        )

    if result.success:
        _try_convert_referral(user_id=submission.user_id)


def _try_convert_referral(*, user_id) -> None:
    try:
        from apps.referrals.services.check_and_convert import check_and_convert_referral

        check_and_convert_referral(user_id=user_id)
    except Exception:
        logger.warning("Referral conversion check failed for user %s", user_id)
