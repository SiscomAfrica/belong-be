from __future__ import annotations

from uuid import UUID

from ninja import Query, Router

from apps.investments.schemas.input_plans import PlanCreateIn, PlanUpdateIn
from apps.investments.schemas.output_plans import PlanListOut, RecurringPlanOut
from apps.investments.selectors.list_user_plans import list_user_plans
from apps.investments.services.create_recurring_plan import create_recurring_plan
from apps.investments.services.pause_recurring_plan import pause_recurring_plan
from apps.investments.services.update_recurring_plan import update_recurring_plan

plans_router = Router(tags=["recurring-plans"])


@plans_router.post("/", response={201: RecurringPlanOut})
def create_plan(request, payload: PlanCreateIn):  # noqa: ANN001, ANN201
    """Create a recurring investment plan for a fund."""
    plan = create_recurring_plan(
        user_id=request.auth.id,
        fund_id=payload.fund_id,
        amount=payload.amount,
        frequency=payload.frequency,
    )
    return 201, plan


@plans_router.get("/", response=PlanListOut)
def list_plans(request, is_active: bool = Query(None)):  # noqa: ANN001, ANN201
    """List the user's recurring investment plans."""
    qs = list_user_plans(user_id=request.auth.id, is_active=is_active)
    return PlanListOut(items=list(qs), count=qs.count())


@plans_router.get("/{plan_id}", response=RecurringPlanOut)
def get_plan(request, plan_id: UUID):  # noqa: ANN001, ANN201
    """Return details for a single recurring plan."""
    from apps.investments.selectors.get_recurring_plan import get_recurring_plan
    return get_recurring_plan(plan_id=plan_id, user_id=request.auth.id)


@plans_router.patch("/{plan_id}", response=RecurringPlanOut)
def update_plan(request, plan_id: UUID, payload: PlanUpdateIn):  # noqa: ANN001, ANN201
    """Update amount or frequency of a recurring plan."""
    return update_recurring_plan(
        plan_id=plan_id,
        user_id=request.auth.id,
        amount=payload.amount,
        frequency=payload.frequency,
    )


@plans_router.delete("/{plan_id}", response={204: None})
def delete_plan(request, plan_id: UUID):  # noqa: ANN001, ANN201
    """Pause and deactivate a recurring plan."""
    pause_recurring_plan(plan_id=plan_id, user_id=request.auth.id)
    return 204, None
