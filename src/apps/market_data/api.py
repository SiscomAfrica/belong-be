from __future__ import annotations

from ninja import Router

from apps.market_data.schemas import ExchangeRateOut, MarketTickerOut
from apps.market_data.selectors.get_exchange_rate import get_exchange_rate
from apps.market_data.selectors.list_exchange_rates import list_exchange_rates
from apps.market_data.selectors.list_market_tickers import list_market_tickers

market_router = Router(tags=["market"], auth=None)


@market_router.get("/rates", response=list[ExchangeRateOut])
def get_rates(request):  # noqa: ANN001, ANN201
    """List all available exchange rates."""
    return list_exchange_rates()


@market_router.get("/rates/{base}/{quote}", response=ExchangeRateOut)
def get_rate(request, base: str, quote: str):  # noqa: ANN001, ANN201
    """Return the exchange rate for a specific currency pair."""
    return get_exchange_rate(base_currency=base, quote_currency=quote)


@market_router.get("/tickers", response=list[MarketTickerOut])
def get_tickers(request):  # noqa: ANN001, ANN201
    """List current market ticker data."""
    return list_market_tickers()
