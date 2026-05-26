from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.referrals.models import CredsLedger


def list_creds_ledger(*, user_id: UUID) -> QuerySet[CredsLedger]:
    return CredsLedger.objects.filter(user_id=user_id).order_by("-created_at")
