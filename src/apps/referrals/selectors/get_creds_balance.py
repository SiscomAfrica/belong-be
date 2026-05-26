from __future__ import annotations

from uuid import UUID

from apps.referrals.models import CredsLedger


def get_creds_balance(*, user_id: UUID) -> int:
    entry = CredsLedger.objects.filter(user_id=user_id).order_by("-created_at").first()
    return entry.balance_after if entry else 0
