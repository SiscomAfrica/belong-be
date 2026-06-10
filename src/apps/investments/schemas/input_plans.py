from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class PlanCreateIn(Schema):
    fund_id: UUID = Field(description="Target fund UUID for recurring investment")
    amount: Decimal = Field(gt=0, description="Recurring investment amount in KES")
    frequency: str = Field(pattern="^(DAILY|WEEKLY|BIWEEKLY|MONTHLY)$", description="Execution frequency")


class PlanUpdateIn(Schema):
    amount: Decimal | None = Field(default=None, gt=0, description="Updated amount in KES")
    frequency: str | None = Field(
        default=None, pattern="^(DAILY|WEEKLY|BIWEEKLY|MONTHLY)$", description="Updated frequency"
    )
