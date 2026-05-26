from __future__ import annotations

from apps.funds.models import Fund


def get_fund_by_slug(*, slug: str) -> Fund | None:
    return Fund.objects.filter(slug=slug, is_active=True).first()
