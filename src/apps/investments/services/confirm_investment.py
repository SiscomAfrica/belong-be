from __future__ import annotations

import logging
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.investments.models import Investment, InvestmentStatus
from apps.investments.services.update_holding import update_holding

logger = logging.getLogger(__name__)


def confirm_investment(*, investment_id: UUID) -> Investment:
    with transaction.atomic():
        investment = (
            Investment.objects.select_for_update()
            .select_related("fund")
            .get(id=investment_id)
        )
        investment.status = InvestmentStatus.CONFIRMED
        investment.confirmed_at = timezone.now()
        investment.save(update_fields=["status", "confirmed_at", "updated_at"])

        update_holding(
            user_id=investment.user_id,
            fund_id=investment.fund_id,
            units=investment.units,
            amount=investment.amount,
        )

    create_audit_log(
        action=AuditAction.INVESTMENT_CONFIRMED,
        actor_id=investment.user_id,
        entity_type="Investment",
        entity_id=investment.id,
        new_values={"status": InvestmentStatus.CONFIRMED},
    )

    _try_convert_referral(user_id=investment.user_id)

    return investment


def _try_convert_referral(*, user_id) -> None:
    try:
        from apps.referrals.services.check_and_convert import check_and_convert_referral

        check_and_convert_referral(user_id=user_id)
    except Exception:
        logger.warning("Referral conversion check failed for user %s", user_id)
