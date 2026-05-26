from __future__ import annotations

from uuid import UUID

from apps.referrals.models import CredsLedger


def award_creds(*, user_id: UUID, amount: int, reason: str) -> CredsLedger:
    last_entry = (
        CredsLedger.objects.filter(user_id=user_id).order_by("-created_at").first()
    )
    previous_balance = last_entry.balance_after if last_entry else 0

    return CredsLedger.objects.create(
        user_id=user_id,
        delta=amount,
        reason=reason,
        balance_after=previous_balance + amount,
    )
