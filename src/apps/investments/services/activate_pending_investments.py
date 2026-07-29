from __future__ import annotations

import logging
from uuid import UUID

from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.investments.models import Investment, InvestmentStatus
from apps.investments.services.confirm_investment import confirm_investment
from apps.notifications.services.create_notification import create_notification

logger = logging.getLogger(__name__)


def activate_pending_investments(*, user_id: UUID) -> int:
    pending = Investment.objects.filter(
        user_id=user_id, status=InvestmentStatus.PENDING_KYC,
    )
    ids = list(pending.values_list("id", flat=True))
    if not ids:
        return 0

    paid_ids = _get_paid_investment_ids(ids)
    unpaid_ids = [i for i in ids if i not in paid_ids]

    if unpaid_ids:
        Investment.objects.filter(id__in=unpaid_ids).update(
            status=InvestmentStatus.PENDING,
        )

    for inv_id in ids:
        if inv_id in paid_ids:
            confirm_investment(investment_id=inv_id)

        new_status = (
            InvestmentStatus.CONFIRMED if inv_id in paid_ids
            else InvestmentStatus.PENDING
        )
        create_audit_log(
            action=AuditAction.INVESTMENT_KYC_ACTIVATED,
            actor_id=user_id,
            entity_type="Investment",
            entity_id=inv_id,
            new_values={"status": new_status},
        )

    create_notification(
        user_id=user_id,
        type="KYC_INVESTMENTS_ACTIVATED",
        title="Investments Activated",
        body="Your identity is verified! Your investments are now active.",
    )
    logger.info("Activated %d pending-KYC investments for user %s", len(ids), user_id)
    return len(ids)


def _get_paid_investment_ids(investment_ids: list[UUID]) -> set[UUID]:
    from apps.payments.models import PaymentStatus, PaymentTransaction

    return set(
        PaymentTransaction.objects.filter(
            investment_id__in=investment_ids,
            status=PaymentStatus.SUCCESS,
        ).values_list("investment_id", flat=True)
    )
