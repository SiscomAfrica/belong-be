from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class PaymentTransactionOut(Schema):
    id: UUID
    investment_id: UUID | None
    provider: str
    status: str
    amount: Decimal
    external_ref: str
    authorization_url: str
    failure_reason: str
    created_at: datetime
    completed_at: datetime | None


class PaymentInitiateOut(Schema):
    transaction: PaymentTransactionOut
    authorization_url: str


class PaymentListOut(Schema):
    items: list[PaymentTransactionOut]
    count: int


class WithdrawalOut(Schema):
    id: UUID
    amount: Decimal
    status: str
    phone_number: str
    created_at: datetime
    processed_at: datetime | None


class WithdrawalListOut(Schema):
    items: list[WithdrawalOut]
    count: int


class WebhookAckOut(Schema):
    result_code: int = 0
    result_desc: str = "Accepted"
