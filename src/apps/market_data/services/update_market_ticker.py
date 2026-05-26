from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from apps.market_data.models import MarketTicker


def update_market_ticker(
    *,
    symbol: str,
    name: str,
    price: Decimal,
    change_pct: Decimal,
    change_value: Decimal,
    currency: str = "USD",
) -> MarketTicker:
    ticker, _created = MarketTicker.objects.update_or_create(
        symbol=symbol,
        defaults={
            "name": name,
            "price": price,
            "change_pct": change_pct,
            "change_value": change_value,
            "currency": currency,
            "fetched_at": timezone.now(),
        },
    )
    return ticker
