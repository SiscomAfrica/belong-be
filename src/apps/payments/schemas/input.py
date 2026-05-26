from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class PaymentInitiateIn(Schema):
    investment_id: UUID
    provider: str
    phone_number: str = ""
    idempotency_key: str = Field(min_length=8, max_length=64)


class WithdrawalCreateIn(Schema):
    amount: Decimal = Field(gt=0)
    phone_number: str
