from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="apps.funds.tasks.calculate_all_fund_performance")
def calculate_all_fund_performance() -> int:
    from apps.funds.models import Fund
    from apps.funds.services.calculate_performance import calculate_performance

    funds = Fund.objects.filter(is_active=True)
    count = 0

    for fund in funds:
        calculate_performance(fund_id=fund.pk)
        count += 1

    logger.info("Calculated performance for %d funds", count)
    return count
