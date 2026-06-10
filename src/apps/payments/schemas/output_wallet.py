from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class WalletOut(Schema):
    id: UUID = Field(description="Wallet identifier")
    balance_ksh: Decimal = Field(description="Wallet balance in KES")
    balance_usd: Decimal = Field(description="Wallet balance converted to USD")
    updated_at: datetime = Field(description="Last balance update timestamp")
