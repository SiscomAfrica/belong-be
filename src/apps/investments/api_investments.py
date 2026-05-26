from __future__ import annotations

from uuid import UUID

from ninja import Query, Router

from apps.investments.schemas import InvestmentCreateIn, InvestmentListOut, InvestmentOut
from apps.investments.selectors.get_investment import get_investment
from apps.investments.selectors.list_user_investments import list_user_investments
from apps.investments.services.create_investment import create_investment

investments_router = Router(tags=["investments"])


@investments_router.post("/", response={201: InvestmentOut})
def create(request, payload: InvestmentCreateIn):  # noqa: ANN001, ANN201
    investment = create_investment(
        user_id=request.auth.id,
        fund_id=payload.fund_id,
        amount=payload.amount,
        idempotency_key=payload.idempotency_key,
    )
    return 201, investment


@investments_router.get("/", response=InvestmentListOut)
def list_investments(  # noqa: ANN001, ANN201
    request,
    status: str | None = Query(None),
    fund_id: UUID | None = Query(None),
):
    qs = list_user_investments(
        user_id=request.auth.id, status=status, fund_id=fund_id
    )
    return {"items": list(qs), "count": qs.count()}


@investments_router.get("/{investment_id}", response=InvestmentOut)
def detail(request, investment_id: UUID):  # noqa: ANN001, ANN201
    return get_investment(investment_id=investment_id, user_id=request.auth.id)
