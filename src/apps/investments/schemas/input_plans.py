from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field

# Mirrors PlanFrequency, which mirrors M-Pesa Ratiba's Frequency enum. A
# cadence Ratiba cannot express is a cadence we cannot collect.
FREQUENCY_PATTERN = (
    "^(ONE_OFF|DAILY|WEEKLY|BIWEEKLY|MONTHLY|BIMONTHLY|QUARTERLY|HALF_YEARLY|YEARLY)$"
)


class PlanCreateIn(Schema):
    fund_id: UUID = Field(description="Target fund UUID for recurring investment")
    amount: Decimal = Field(gt=0, description="Recurring investment amount in KES")
    frequency: str = Field(
        pattern=FREQUENCY_PATTERN,
        description="Contribution cadence; mirrors M-Pesa Ratiba frequencies",
    )


class PlanUpdateIn(Schema):
    amount: Decimal | None = Field(default=None, gt=0, description="Updated amount in KES")
    frequency: str | None = Field(
        default=None, pattern=FREQUENCY_PATTERN, description="Updated frequency",
    )
