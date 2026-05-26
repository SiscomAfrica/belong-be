from __future__ import annotations

from uuid import UUID

from apps.investments.exceptions import GoalNotFoundError
from apps.investments.models.investment_goal import InvestmentGoal


def get_investment_goal(*, goal_id: UUID, user_id: UUID) -> InvestmentGoal:
    try:
        return InvestmentGoal.objects.select_related("fund").get(
            id=goal_id, user_id=user_id
        )
    except InvestmentGoal.DoesNotExist:
        raise GoalNotFoundError()
