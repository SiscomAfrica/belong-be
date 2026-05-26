from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from apps.market_data.models import ExchangeRate


def update_exchange_rate(
    *,
    base_currency: str,
    quote_currency: str,
    rate: Decimal,
    source: str,
) -> ExchangeRate:
    exchange_rate, _created = ExchangeRate.objects.update_or_create(
        base_currency=base_currency,
        quote_currency=quote_currency,
        defaults={
            "rate": rate,
            "source": source,
            "fetched_at": timezone.now(),
        },
    )
    return exchange_rate
