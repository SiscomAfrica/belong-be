from __future__ import annotations

import logging
from uuid import UUID

from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.investments.models import Investment, InvestmentStatus
from apps.notifications.services.create_notification import create_notification

logger = logging.getLogger(__name__)


def activate_pending_investments(*, user_id: UUID) -> int:
    pending = Investment.objects.filter(
        user_id=user_id, status=InvestmentStatus.PENDING_KYC,
    )
    ids = list(pending.values_list("id", flat=True))
    if not ids:
        return 0

    count = pending.update(status=InvestmentStatus.PENDING)

    for inv_id in ids:
        create_audit_log(
            action=AuditAction.INVESTMENT_KYC_ACTIVATED,
            actor_id=user_id,
            entity_type="Investment",
            entity_id=inv_id,
            new_values={"status": InvestmentStatus.PENDING},
        )

    create_notification(
        user_id=user_id,
        type="KYC_INVESTMENTS_ACTIVATED",
        title="Investments Activated",
        body="Your identity is verified! Your investments are now active.",
    )
    logger.info("Activated %d pending-KYC investments for user %s", count, user_id)
    return count
