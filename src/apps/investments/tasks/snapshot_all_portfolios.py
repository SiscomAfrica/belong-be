from __future__ import annotations

import logging

from celery import shared_task

from apps.investments.models import Holding
from apps.investments.services.record_portfolio_snapshot import record_portfolio_snapshot

logger = logging.getLogger(__name__)


@shared_task(name="apps.investments.tasks.snapshot_all_portfolios")
def snapshot_all_portfolios() -> int:
    user_ids = (
        Holding.objects.values_list("user_id", flat=True).distinct()
    )

    count = 0
    for user_id in user_ids:
        record_portfolio_snapshot(user_id=user_id)
        count += 1

    logger.info("Recorded %d portfolio snapshots", count)
    return count
