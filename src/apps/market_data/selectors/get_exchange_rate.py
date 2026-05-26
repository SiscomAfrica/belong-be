from __future__ import annotations

from apps.common.exceptions import NotFoundError
from apps.market_data.models import ExchangeRate


def get_exchange_rate(*, base_currency: str, quote_currency: str) -> ExchangeRate:
    try:
        return ExchangeRate.objects.get(
            base_currency=base_currency,
            quote_currency=quote_currency,
        )
    except ExchangeRate.DoesNotExist:
        raise NotFoundError(
            f"Exchange rate {base_currency}/{quote_currency} not found"
        )
