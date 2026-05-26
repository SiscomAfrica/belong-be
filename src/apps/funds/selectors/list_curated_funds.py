from __future__ import annotations

from django.db.models import QuerySet

from apps.funds.models import Fund

INVESTOR_RISK_MAP: dict[str, list[int]] = {
    "CONSERVATIVE": [1, 2],
    "MODERATE": [2, 3],
    "INTERMEDIATE": [3],
    "AGGRESSIVE": [3, 4],
    "HIGH_RISK": [4, 5],
}


def list_curated_funds(*, investor_type: str) -> QuerySet[Fund]:
    risk_levels = INVESTOR_RISK_MAP.get(investor_type, [3])
    return Fund.objects.filter(
        is_active=True,
        risk_level__in=risk_levels,
    )
