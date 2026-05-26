from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class InvestmentCreateIn(Schema):
    fund_id: UUID
    amount: Decimal = Field(gt=0)
    idempotency_key: str = Field(min_length=8, max_length=64)
