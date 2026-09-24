from __future__ import annotations

import logging
from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.common.observability import report_exception
from apps.kyc.models import KYCStatus, KYCSubmission
from apps.notifications.services.create_notification import create_notification

logger = logging.getLogger(__name__)


def apply_kyc_decision(
    *, submission: KYCSubmission, verified: bool, result_text: str = "",
) -> KYCSubmission:
    """Everything that must happen when a submission is decided.

    Both routes share this so they cannot drift apart. They already had: the
    Smile Identity webhook did all of it, while approving in the admin only
    wrote the status — with a queryset update, which skips save() and any
    signal with it. Verification here is manual, so the webhook never fires
    and the admin was the only route that ran.

    What manual approval silently skipped was the part that matters most:
    an investment paid for before KYC cleared sits in PENDING_KYC, and
    settle_successful_payment deliberately leaves it there for this step to
    finish. Nothing finished it. The payment succeeded, the member was
    verified, and their money bought nothing.
    """
    new_status = KYCStatus.VERIFIED if verified else KYCStatus.REJECTED
    submission.status = new_status
    submission.result_text = result_text
    submission.save(update_fields=["status", "result_text", "updated_at"])

    create_audit_log(
        action=AuditAction.KYC_APPROVED if verified else AuditAction.KYC_REJECTED,
        entity_type="KYCSubmission",
        entity_id=submission.id,
        actor_id=submission.user_id,
        new_values={"status": new_status},
    )
    create_notification(
        user_id=submission.user_id,
        type="KYC_APPROVED" if verified else "KYC_REJECTED",
        title="KYC Verified" if verified else "KYC Rejected",
        body=(
            "Your identity has been verified successfully."
            if verified
            else f"Your KYC was rejected: {result_text}" if result_text
            else "Your KYC was rejected."
        ),
    )

    if verified:
        try_activate_investments(user_id=submission.user_id)
        try_convert_referral(user_id=submission.user_id)

    return submission


def try_activate_investments(*, user_id: UUID) -> None:
    """Confirm whatever was already paid for, and release the rest to PENDING."""
    try:
        from apps.investments.services.activate_pending_investments import (
            activate_pending_investments,
        )

        activate_pending_investments(user_id=user_id)
    except Exception:
        # The decision is already recorded, so re-raising would fail a webhook
        # the provider would then retry, or an admin action that half-applied.
        # But the user is left with investments stuck in PENDING_KYC, which is
        # money not working — this needs to reach someone, not a log file.
        report_exception(
            message="Investment activation failed after KYC verification",
            logger_=logger,
            user_id=user_id,
        )


def try_convert_referral(*, user_id: UUID) -> None:
    try:
        from apps.referrals.services.check_and_convert import check_and_convert_referral

        check_and_convert_referral(user_id=user_id)
    except Exception:
        report_exception(
            message="Referral conversion failed after KYC verification",
            logger_=logger,
            user_id=user_id,
        )
