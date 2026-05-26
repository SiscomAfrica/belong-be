from __future__ import annotations

from uuid import UUID

from django.db import transaction

from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.investments.models import Investment, InvestmentStatus


def cancel_investment(*, investment_id: UUID, user_id: UUID) -> Investment:
    with transaction.atomic():
        investment = (
            Investment.objects.select_for_update()
            .get(id=investment_id, user_id=user_id, status=InvestmentStatus.PENDING)
        )
        investment.status = InvestmentStatus.CANCELLED
        investment.save(update_fields=["status", "updated_at"])

    create_audit_log(
        action=AuditAction.INVESTMENT_CANCELLED,
        actor_id=user_id,
        entity_type="Investment",
        entity_id=investment.id,
        new_values={"status": InvestmentStatus.CANCELLED},
    )

    return investment
