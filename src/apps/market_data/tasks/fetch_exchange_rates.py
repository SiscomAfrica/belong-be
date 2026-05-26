from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="apps.market_data.tasks.fetch_exchange_rates")
def fetch_exchange_rates() -> None:
    """Stub: will integrate with CBK/forex API later."""
    logger.info("fetch_exchange_rates: stub — no external API configured yet")
