from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class PaymentInitiateIn(Schema):
    investment_id: UUID = Field(description="Investment UUID to pay for")
    provider: str = Field(description="Payment provider: MPESA | PAYSTACK")
    phone_number: str = Field(default="", description="M-Pesa phone number (required for MPESA)")
    idempotency_key: str = Field(min_length=8, max_length=64, description="Client-generated unique key to prevent duplicate payments")


class WithdrawalCreateIn(Schema):
    amount: Decimal = Field(gt=0, description="Withdrawal amount in KES (must be > 0)")
    phone_number: str = Field(description="M-Pesa phone number to receive funds")


class WalletTopUpIn(Schema):
    """Fund the wallet directly, with no investment attached.

    Separate from PaymentInitiateIn rather than making its investment_id
    optional: every existing caller of /payments/initiate/ must keep being
    forced to name an investment, so a client bug cannot turn a purchase into
    an untracked wallet credit.
    """

    amount: Decimal = Field(gt=0, description="Amount to add to the wallet in KES")
    provider: str = Field(default="MPESA", description="Payment provider: MPESA | PAYSTACK")
    phone_number: str = Field(default="", description="M-Pesa phone number (required for MPESA)")
    idempotency_key: str = Field(
        min_length=8, max_length=64,
        description="Client-generated unique key to prevent duplicate top-ups",
    )
