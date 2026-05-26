from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class PlanCreateIn(Schema):
    fund_id: UUID
    amount: Decimal = Field(gt=0)
    frequency: str = Field(pattern="^(DAILY|WEEKLY|BIWEEKLY|MONTHLY)$")


class PlanUpdateIn(Schema):
    amount: Decimal | None = Field(default=None, gt=0)
    frequency: str | None = Field(
        default=None, pattern="^(DAILY|WEEKLY|BIWEEKLY|MONTHLY)$"
    )
