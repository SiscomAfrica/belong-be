from __future__ import annotations

from uuid import UUID

from ninja import Query, Router

from apps.investments.schemas import (
    HoldingDetailOut,
    HoldingOut,
    PortfolioSnapshotOut,
    PortfolioSummaryOut,
)
from apps.investments.selectors.get_holding import get_holding
from apps.investments.selectors.get_portfolio_summary import get_portfolio_summary
from apps.investments.selectors.list_portfolio_snapshots import list_portfolio_snapshots
from apps.investments.selectors.list_user_holdings import list_user_holdings

portfolio_router = Router(tags=["portfolio"])


@portfolio_router.get("/", response=PortfolioSummaryOut)
def summary(request):  # noqa: ANN001, ANN201
    return get_portfolio_summary(user_id=request.auth.id)


@portfolio_router.get("/holdings", response=list[HoldingOut])
def holdings(request):  # noqa: ANN001, ANN201
    return list_user_holdings(user_id=request.auth.id)


@portfolio_router.get("/holdings/{fund_id}", response=HoldingDetailOut)
def holding_detail(request, fund_id: UUID):  # noqa: ANN001, ANN201
    return get_holding(user_id=request.auth.id, fund_id=fund_id)


@portfolio_router.get("/performance", response=list[PortfolioSnapshotOut])
def performance(request, days: int = Query(30)):  # noqa: ANN001, ANN201
    return list_portfolio_snapshots(user_id=request.auth.id, days=days)
