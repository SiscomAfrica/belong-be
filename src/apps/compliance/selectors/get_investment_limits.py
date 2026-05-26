from __future__ import annotations

from apps.compliance.models import InvestmentLimit


def get_investment_limits(*, kyc_tier: str) -> InvestmentLimit | None:
    return InvestmentLimit.objects.filter(kyc_tier=kyc_tier).first()
