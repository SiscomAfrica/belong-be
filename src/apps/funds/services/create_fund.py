from __future__ import annotations

from decimal import Decimal

from apps.funds.models import Fund


def create_fund(
    *,
    name: str,
    slug: str,
    description: str,
    fund_type: str,
    category: str,
    risk_level: int,
    currency: str,
    minimum_investment: Decimal,
    lock_in_days: int = 0,
    projected_annual_return: Decimal,
    effective_annual_yield: Decimal,
    annualized_daily_yield: Decimal,
    hero_image_url: str = "",
    metadata: dict | None = None,
) -> Fund:
    return Fund.objects.create(
        name=name,
        slug=slug,
        description=description,
        fund_type=fund_type,
        category=category,
        risk_level=risk_level,
        currency=currency,
        minimum_investment=minimum_investment,
        lock_in_days=lock_in_days,
        projected_annual_return=projected_annual_return,
        effective_annual_yield=effective_annual_yield,
        annualized_daily_yield=annualized_daily_yield,
        hero_image_url=hero_image_url,
        metadata=metadata or {},
    )
