from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.referrals.models import Referral


def list_referral_history(*, user_id: UUID) -> QuerySet[Referral]:
    return (
        Referral.objects.filter(referrer_id=user_id)
        .select_related("referred_user")
        .order_by("-created_at")
    )
