from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class WalletOut(Schema):
    id: UUID
    balance_ksh: Decimal
    balance_usd: Decimal
    updated_at: datetime
