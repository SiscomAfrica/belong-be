from __future__ import annotations

from uuid import UUID

from django.db.models import Sum

from apps.referrals.models import CredsLedger, Referral, ReferralStatus


def get_referral_stats(*, user_id: UUID) -> dict:
    referrals = Referral.objects.filter(referrer_id=user_id)
    total_referrals = referrals.count()
    total_conversions = referrals.filter(status=ReferralStatus.CONVERTED).count()
    total_creds = (
        CredsLedger.objects.filter(user_id=user_id).aggregate(s=Sum("delta"))["s"] or 0
    )
    return {
        "total_referrals": total_referrals,
        "total_conversions": total_conversions,
        "total_creds": total_creds,
    }
