from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="apps.market_data.tasks.fetch_market_tickers")
def fetch_market_tickers() -> None:
    """Stub: will integrate with market data API later."""
    logger.info("fetch_market_tickers: stub — no external API configured yet")
