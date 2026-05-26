from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.investments.models import Investment, InvestmentStatus

logger = logging.getLogger(__name__)


@shared_task(name="apps.compliance.tasks.generate_monthly_statements")
def generate_monthly_statements() -> None:
    from apps.compliance.services.generate_statement import generate_statement
    from apps.notifications.services.create_notification import create_notification

    now = timezone.now()
    if now.month == 1:
        year, month = now.year - 1, 12
    else:
        year, month = now.year, now.month - 1

    user_ids = (
        Investment.objects.filter(status=InvestmentStatus.CONFIRMED)
        .values_list("user_id", flat=True)
        .distinct()
    )

    for user_id in user_ids:
        try:
            generate_statement(user_id=user_id, year=year, month=month)
            create_notification(
                user_id=user_id,
                type="STATEMENT_READY",
                title="Monthly Statement Ready",
                body=f"Your statement for {year}-{month:02d} is ready.",
            )
        except Exception:
            logger.exception("Failed to generate statement for user %s", user_id)
