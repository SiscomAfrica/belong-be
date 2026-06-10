from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class ExchangeRateOut(Schema):
    id: UUID = Field(description="Rate record identifier")
    base_currency: str = Field(description="Base currency code (e.g. USD)")
    quote_currency: str = Field(description="Quote currency code (e.g. KES)")
    rate: Decimal = Field(description="Exchange rate (1 base = rate quote)")
    source: str = Field(description="Rate data source provider")
    fetched_at: datetime = Field(description="When the rate was fetched")


class MarketTickerOut(Schema):
    id: UUID = Field(description="Ticker record identifier")
    symbol: str = Field(description="Ticker symbol (e.g. AAPL, BTC)")
    name: str = Field(description="Asset display name")
    price: Decimal = Field(description="Current price")
    change_pct: Decimal = Field(description="Percentage change from previous close")
    change_value: Decimal = Field(description="Absolute value change from previous close")
    currency: str = Field(description="Price currency code")
    fetched_at: datetime = Field(description="When the ticker data was fetched")
