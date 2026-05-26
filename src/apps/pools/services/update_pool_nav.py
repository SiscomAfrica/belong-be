from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.funds.services import record_nav
from apps.pools.models import Pool
from apps.pools.selectors import get_pool


def update_pool_nav(
    *, fund_id: UUID, nav_per_unit: Decimal, actor_id: UUID
) -> Pool:
    pool = get_pool(fund_id=fund_id)
    old_nav = pool.nav_per_unit

    pool.nav_per_unit = nav_per_unit
    pool.total_aum = pool.total_units * nav_per_unit
    pool.save(update_fields=["nav_per_unit", "total_aum", "updated_at"])

    daily_change_pct = Decimal("0")
    if old_nav > 0:
        daily_change_pct = ((nav_per_unit - old_nav) / old_nav) * 100

    record_nav(
        fund_id=fund_id,
        date=date.today(),
        nav_value=nav_per_unit,
        daily_change_pct=daily_change_pct,
    )

    create_audit_log(
        action=AuditAction.NAV_UPDATED,
        actor_id=actor_id,
        entity_type="Pool",
        entity_id=pool.id,
        old_values={"nav_per_unit": str(old_nav)},
        new_values={"nav_per_unit": str(nav_per_unit)},
    )

    return pool
