from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.db.models import Sum
from django.utils import timezone

from apps.compliance.exceptions import InvestmentLimitExceededError
from apps.compliance.models import InvestmentLimit
from apps.compliance.services.get_user_tier import get_user_tier
from apps.investments.models import Investment, InvestmentStatus


def check_investment_limit(*, user_id: UUID, amount: Decimal) -> None:
    tier = get_user_tier(user_id=user_id)
    limit = InvestmentLimit.objects.filter(kyc_tier=tier).first()

    if limit is None:
        return

    if amount > limit.max_per_transaction:
        raise InvestmentLimitExceededError(
            f"Amount {amount} exceeds per-transaction limit of {limit.max_per_transaction}.",
        )

    now = timezone.now()
    monthly_total = (
        Investment.objects.filter(
            user_id=user_id,
            status=InvestmentStatus.CONFIRMED,
            confirmed_at__year=now.year,
            confirmed_at__month=now.month,
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )

    if monthly_total + amount > limit.max_per_month:
        raise InvestmentLimitExceededError(
            f"Monthly total {monthly_total + amount} exceeds limit of {limit.max_per_month}.",
        )
