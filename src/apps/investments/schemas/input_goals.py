from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class GoalCreateIn(Schema):
    fund_id: UUID
    target_amount: Decimal = Field(gt=0)
    target_date: date


class GoalUpdateIn(Schema):
    target_amount: Decimal | None = Field(default=None, gt=0)
    target_date: date | None = None
