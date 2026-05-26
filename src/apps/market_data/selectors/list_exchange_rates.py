from __future__ import annotations

from django.db.models import QuerySet

from apps.market_data.models import ExchangeRate


def list_exchange_rates() -> QuerySet[ExchangeRate]:
    return ExchangeRate.objects.order_by("base_currency")
