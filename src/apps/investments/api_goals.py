from __future__ import annotations

from uuid import UUID

from ninja import Router

from apps.investments.schemas.input_goals import GoalCreateIn, GoalUpdateIn
from apps.investments.schemas.output_goals import GoalListOut, InvestmentGoalOut
from apps.investments.selectors.get_investment_goal import get_investment_goal
from apps.investments.selectors.list_user_goals import list_user_goals
from apps.investments.services.create_investment_goal import create_investment_goal
from apps.investments.services.update_investment_goal import update_investment_goal

goals_router = Router(tags=["investment-goals"])


@goals_router.post("/", response={201: InvestmentGoalOut})
def create_goal(request, payload: GoalCreateIn):  # noqa: ANN001, ANN201
    goal = create_investment_goal(
        user_id=request.auth.id,
        fund_id=payload.fund_id,
        target_amount=payload.target_amount,
        target_date=payload.target_date,
    )
    return 201, goal


@goals_router.get("/", response=GoalListOut)
def list_goals(request):  # noqa: ANN001, ANN201
    qs = list_user_goals(user_id=request.auth.id)
    return GoalListOut(items=list(qs), count=qs.count())


@goals_router.get("/{goal_id}", response=InvestmentGoalOut)
def get_goal(request, goal_id: UUID):  # noqa: ANN001, ANN201
    return get_investment_goal(goal_id=goal_id, user_id=request.auth.id)


@goals_router.patch("/{goal_id}", response=InvestmentGoalOut)
def update_goal(request, goal_id: UUID, payload: GoalUpdateIn):  # noqa: ANN001, ANN201
    return update_investment_goal(
        goal_id=goal_id,
        user_id=request.auth.id,
        target_amount=payload.target_amount,
        target_date=payload.target_date,
    )
