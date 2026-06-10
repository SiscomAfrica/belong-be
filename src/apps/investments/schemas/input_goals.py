from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class GoalCreateIn(Schema):
    fund_id: UUID = Field(description="Target fund UUID for the goal")
    target_amount: Decimal = Field(gt=0, description="Goal target amount in KES")
    target_date: date = Field(description="Target date to reach the goal")


class GoalUpdateIn(Schema):
    target_amount: Decimal | None = Field(default=None, gt=0, description="Updated target amount in KES")
    target_date: date | None = Field(default=None, description="Updated target date")
