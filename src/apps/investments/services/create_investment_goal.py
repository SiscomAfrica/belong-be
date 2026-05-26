from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.investments.models.investment_goal import InvestmentGoal


def create_investment_goal(
    *,
    user_id: UUID,
    fund_id: UUID,
    target_amount: Decimal,
    target_date: date,
) -> InvestmentGoal:
    goal = InvestmentGoal.objects.create(
        user_id=user_id,
        fund_id=fund_id,
        target_amount=target_amount,
        target_date=target_date,
    )

    create_audit_log(
        action=AuditAction.GOAL_CREATED,
        actor_id=user_id,
        entity_type="InvestmentGoal",
        entity_id=goal.id,
        new_values={"target_amount": str(target_amount)},
    )
    return goal
