from __future__ import annotations

from uuid import UUID

from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.referrals.exceptions import InvalidReferralCodeError, SelfReferralError
from apps.referrals.models import Referral
from apps.users.models import User


def create_referral(*, referrer_code: str, referred_user_id: UUID) -> Referral:
    referrer = User.objects.filter(referral_code=referrer_code).first()
    if referrer is None:
        raise InvalidReferralCodeError()

    if referrer.id == referred_user_id:
        raise SelfReferralError()

    referral = Referral.objects.create(
        referrer=referrer,
        referred_user_id=referred_user_id,
    )

    create_audit_log(
        action=AuditAction.REFERRAL_CREATED,
        actor_id=referred_user_id,
        entity_type="Referral",
        entity_id=referral.id,
        new_values={"referrer_id": str(referrer.id)},
    )

    return referral
