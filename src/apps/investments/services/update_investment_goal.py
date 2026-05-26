from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from apps.investments.models.investment_goal import InvestmentGoal
from apps.investments.selectors.get_investment_goal import get_investment_goal


def update_investment_goal(
    *,
    goal_id: UUID,
    user_id: UUID,
    target_amount: Decimal | None = None,
    target_date: date | None = None,
) -> InvestmentGoal:
    goal = get_investment_goal(goal_id=goal_id, user_id=user_id)
    update_fields = ["updated_at"]

    if target_amount is not None:
        goal.target_amount = target_amount
        update_fields.append("target_amount")

    if target_date is not None:
        goal.target_date = target_date
        update_fields.append("target_date")

    goal.save(update_fields=update_fields)
    return goal
