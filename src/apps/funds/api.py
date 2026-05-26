from __future__ import annotations

from uuid import UUID

from ninja import Query, Router

from apps.funds.schemas import (
    FundDetailOut,
    FundListOut,
    FundNAVOut,
    FundOut,
    ProjectionIn,
    ProjectionOut,
)
from apps.funds.selectors.get_fund import get_fund
from apps.funds.selectors.list_curated_funds import list_curated_funds
from apps.funds.selectors.list_fund_nav import list_fund_nav
from apps.funds.selectors.list_funds import list_funds
from apps.funds.selectors.list_trending_funds import list_trending_funds
from apps.funds.services.calculate_projection import calculate_projection

funds_router = Router(tags=["funds"])


@funds_router.get("/", response=FundListOut, auth=None)
def list_all_funds(  # noqa: ANN001, ANN201
    request,
    fund_type: str | None = Query(None),
    category: str | None = Query(None),
    risk_level: int | None = Query(None),
    search: str | None = Query(None),
):
    qs = list_funds(
        fund_type=fund_type,
        category=category,
        risk_level=risk_level,
        search=search,
    )
    return {"items": list(qs), "count": qs.count()}


@funds_router.get("/trending", response=list[FundOut], auth=None)
def trending(request):  # noqa: ANN001, ANN201
    return list_trending_funds()


@funds_router.get("/curated", response=list[FundOut])
def curated(request):  # noqa: ANN001, ANN201
    return list_curated_funds(investor_type=request.auth.investor_type)


@funds_router.post("/projection", response=ProjectionOut, auth=None)
def projection(request, payload: ProjectionIn):  # noqa: ANN001, ANN201
    return calculate_projection(
        goal=payload.goal,
        contribution=payload.contribution,
        frequency=payload.frequency,
        years=payload.years,
        annual_return_pct=payload.annual_return_pct,
    )


@funds_router.get("/{fund_id}", response=FundDetailOut, auth=None)
def fund_detail(request, fund_id: UUID):  # noqa: ANN001, ANN201
    return get_fund(fund_id=fund_id)


@funds_router.get("/{fund_id}/nav", response=list[FundNAVOut], auth=None)
def fund_nav(request, fund_id: UUID, days: int = Query(30)):  # noqa: ANN001, ANN201
    return list_fund_nav(fund_id=fund_id, days=days)
