from __future__ import annotations

from decimal import Decimal

from apps.market_data.models import ExchangeRate


def convert_currency(
    *, amount: Decimal, from_currency: str, to_currency: str
) -> Decimal:
    if from_currency == to_currency:
        return amount

    direct = ExchangeRate.objects.filter(
        base_currency=from_currency, quote_currency=to_currency
    ).first()
    if direct:
        return amount * direct.rate

    inverse = ExchangeRate.objects.filter(
        base_currency=to_currency, quote_currency=from_currency
    ).first()
    if inverse and inverse.rate > 0:
        return amount / inverse.rate

    raise ValueError(f"No exchange rate found for {from_currency}/{to_currency}")
