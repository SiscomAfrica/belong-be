from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class PaymentTransactionOut(Schema):
    id: UUID = Field(description="Transaction identifier")
    investment_id: UUID | None = Field(default=None, description="Associated investment UUID")
    provider: str = Field(description="Payment provider: MPESA | PAYSTACK")
    status: str = Field(description="Status: PENDING | SUCCESS | FAILED")
    amount: Decimal = Field(description="Transaction amount in KES")
    external_ref: str = Field(description="Provider-side reference ID")
    authorization_url: str = Field(description="Redirect URL for card payments (Paystack)")
    failure_reason: str = Field(description="Human-readable failure reason if failed")
    created_at: datetime = Field(description="Transaction creation timestamp")
    completed_at: datetime | None = Field(default=None, description="When the transaction completed")


class PaymentInitiateOut(Schema):
    transaction: PaymentTransactionOut = Field(description="Created payment transaction")
    authorization_url: str = Field(description="URL to redirect user for payment authorization")


class PaymentListOut(Schema):
    items: list[PaymentTransactionOut] = Field(description="List of transactions")
    count: int = Field(description="Total number of matching transactions")


class WithdrawalOut(Schema):
    id: UUID = Field(description="Withdrawal request identifier")
    amount: Decimal = Field(description="Withdrawal amount in KES")
    status: str = Field(description="Status: PENDING | PROCESSING | SUCCESS | FAILED")
    phone_number: str = Field(description="Recipient M-Pesa phone number")
    created_at: datetime = Field(description="Request creation timestamp")
    processed_at: datetime | None = Field(default=None, description="When withdrawal was processed")


class WithdrawalListOut(Schema):
    items: list[WithdrawalOut] = Field(description="List of withdrawal requests")
    count: int = Field(description="Total number of withdrawals")


class WebhookAckOut(Schema):
    result_code: int = Field(default=0, description="Result code (0 = accepted)")
    result_desc: str = Field(default="Accepted", description="Human-readable result description")
