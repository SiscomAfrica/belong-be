from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.payments.models import PaymentTransaction


def list_user_payments(
    *,
    user_id: UUID,
    status: str | None = None,
    provider: str | None = None,
) -> QuerySet[PaymentTransaction]:
    qs = PaymentTransaction.objects.filter(user_id=user_id).select_related(
        "investment__fund",
    )

    if status:
        qs = qs.filter(status=status)
    if provider:
        qs = qs.filter(provider=provider)

    return qs
