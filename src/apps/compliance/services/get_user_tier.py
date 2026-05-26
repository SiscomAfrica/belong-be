from __future__ import annotations

from uuid import UUID

from apps.compliance.models import KYCTier
from apps.kyc.models import KYCStatus, KYCSubmission
from apps.users.models import User


def get_user_tier(*, user_id: UUID) -> str:
    kyc = KYCSubmission.objects.filter(user_id=user_id).order_by("-created_at").first()
    if kyc is None or kyc.status != KYCStatus.VERIFIED:
        return KYCTier.UNVERIFIED

    user = User.objects.get(pk=user_id)
    if user.is_onboarded:
        return KYCTier.FULL

    return KYCTier.BASIC
