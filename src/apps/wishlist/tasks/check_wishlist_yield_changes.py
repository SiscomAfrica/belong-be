from __future__ import annotations

import logging
from decimal import Decimal

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="apps.wishlist.tasks.check_wishlist_yield_changes")
def check_wishlist_yield_changes() -> int:
    from apps.funds.models import FundNAV
    from apps.notifications.models import Notification, NotificationType
    from apps.wishlist.models import WishlistItem

    fund_ids = (
        WishlistItem.objects.values_list("fund_id", flat=True).distinct()
    )
    alerts_sent = 0

    for fund_id in fund_ids:
        navs = list(
            FundNAV.objects.filter(fund_id=fund_id)
            .order_by("-date")[:2]
        )
        if len(navs) < 2:
            continue

        latest, previous = navs[0], navs[1]
        if previous.nav_value == 0:
            continue

        change_pct = abs(
            (latest.nav_value - previous.nav_value) / previous.nav_value * 100
        )
        if change_pct <= Decimal("1"):
            continue

        user_ids = WishlistItem.objects.filter(
            fund_id=fund_id
        ).values_list("user_id", flat=True)

        direction = "up" if latest.nav_value > previous.nav_value else "down"
        notifications = [
            Notification(
                user_id=uid,
                type=NotificationType.YIELD_ALERT,
                title="Yield alert",
                body=f"A fund on your wishlist moved {direction} {change_pct:.2f}%.",
            )
            for uid in user_ids
        ]
        Notification.objects.bulk_create(notifications)
        alerts_sent += len(notifications)

    logger.info("Sent %d yield alerts", alerts_sent)
    return alerts_sent
