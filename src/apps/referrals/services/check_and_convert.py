from __future__ import annotations

import logging
from uuid import UUID

from django.utils import timezone

from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.investments.models import Investment, InvestmentStatus
from apps.kyc.models import KYCStatus, KYCSubmission
from apps.notifications.services.create_notification import create_notification
from apps.referrals.models import Referral, ReferralStatus
from apps.referrals.services.award_creds import award_creds

logger = logging.getLogger(__name__)

REFERRAL_CREDS_AMOUNT = 100


def check_and_convert_referral(*, user_id: UUID) -> None:
    referral = Referral.objects.filter(
        referred_user_id=user_id, status=ReferralStatus.PENDING,
    ).first()

    if referral is None:
        return

    kyc_verified = KYCSubmission.objects.filter(
        user_id=user_id, status=KYCStatus.VERIFIED,
    ).exists()
    has_investment = Investment.objects.filter(
        user_id=user_id, status=InvestmentStatus.CONFIRMED,
    ).exists()

    if not (kyc_verified and has_investment):
        return

    referral.status = ReferralStatus.CONVERTED
    referral.converted_at = timezone.now()
    referral.creds_awarded = REFERRAL_CREDS_AMOUNT
    referral.save(update_fields=["status", "converted_at", "creds_awarded", "updated_at"])

    award_creds(
        user_id=referral.referrer_id,
        amount=REFERRAL_CREDS_AMOUNT,
        reason=f"Referral converted: {user_id}",
    )

    create_audit_log(
        action=AuditAction.REFERRAL_CONVERTED,
        actor_id=user_id,
        entity_type="Referral",
        entity_id=referral.id,
        new_values={"creds_awarded": REFERRAL_CREDS_AMOUNT},
    )

    create_notification(
        user_id=referral.referrer_id,
        type="REFERRAL_CONVERTED",
        title="Referral Converted!",
        body=f"Your referral earned you {REFERRAL_CREDS_AMOUNT} Belong Creds.",
    )
