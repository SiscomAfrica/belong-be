from __future__ import annotations

from typing import Any
from uuid import UUID

from apps.funds.models import Fund
from apps.funds.selectors.get_fund import get_fund


def update_fund(*, fund_id: UUID, **fields: Any) -> Fund:
    fund = get_fund(fund_id=fund_id)

    for field, value in fields.items():
        setattr(fund, field, value)

    fund.save(update_fields=[*fields.keys(), "updated_at"])
    return fund
