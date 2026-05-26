from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.investments.models import Investment


def list_user_investments(
    *,
    user_id: UUID,
    status: str | None = None,
    fund_id: UUID | None = None,
) -> QuerySet[Investment]:
    qs = Investment.objects.filter(user_id=user_id).select_related("fund")

    if status:
        qs = qs.filter(status=status)
    if fund_id:
        qs = qs.filter(fund_id=fund_id)

    return qs
