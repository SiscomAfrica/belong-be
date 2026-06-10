from __future__ import annotations

from uuid import UUID

from ninja import Router

from apps.pools.schemas import PoolListOut, PoolNavUpdateIn, PoolOut
from apps.pools.selectors import get_pool, list_pools
from apps.pools.services import update_pool_nav

pools_router = Router(tags=["pools"])


@pools_router.post("/{fund_id}/update-nav", response=PoolOut)
def update_nav(request, fund_id: UUID, payload: PoolNavUpdateIn):  # noqa: ANN001, ANN201
    """Update the NAV per unit for a fund pool. Staff only."""
    if not request.auth.is_staff:
        from apps.common.exceptions import PermissionDeniedError
        raise PermissionDeniedError("Staff access required.")
    pool = update_pool_nav(
        fund_id=fund_id,
        nav_per_unit=payload.nav_per_unit,
        actor_id=request.auth.id,
    )
    return pool


@pools_router.get("/", response=PoolListOut)
def list_all_pools(request):  # noqa: ANN001, ANN201
    """List all investment pools with current NAV data."""
    qs = list_pools()
    return PoolListOut(items=list(qs), count=qs.count())


@pools_router.get("/{fund_id}", response=PoolOut)
def get_pool_detail(request, fund_id: UUID):  # noqa: ANN001, ANN201
    """Return pool details for a specific fund."""
    return get_pool(fund_id=fund_id)
