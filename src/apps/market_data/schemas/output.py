from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class ExchangeRateOut(Schema):
    id: UUID
    base_currency: str
    quote_currency: str
    rate: Decimal
    source: str
    fetched_at: datetime


class MarketTickerOut(Schema):
    id: UUID
    symbol: str
    name: str
    price: Decimal
    change_pct: Decimal
    change_value: Decimal
    currency: str
    fetched_at: datetime
