from __future__ import annotations

from django.db.models import QuerySet

from apps.market_data.models import MarketTicker


def list_market_tickers() -> QuerySet[MarketTicker]:
    return MarketTicker.objects.order_by("symbol")
