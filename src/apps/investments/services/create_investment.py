from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.compliance.services.check_investment_limit import check_investment_limit
from apps.funds.models import Fund
from apps.funds.selectors.get_latest_fund_nav import get_latest_fund_nav
from apps.investments.exceptions import (
    BelowMinimumInvestmentError,
    FundNotActiveError,
    NoNAVDataError,
)
from apps.investments.models import Investment, InvestmentStatus
from apps.kyc.models import KYCStatus
from apps.kyc.selectors.get_kyc_status import get_kyc_status


def _resolve_investment_status(*, user_id: UUID) -> str:
    kyc = get_kyc_status(user_id=user_id)
    if kyc["status"] == KYCStatus.VERIFIED:
        return InvestmentStatus.PENDING
    return InvestmentStatus.PENDING_KYC


def create_investment(
    *, user_id: UUID, fund_id: UUID, amount: Decimal, idempotency_key: str
) -> Investment:
    existing = Investment.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing

    status = _resolve_investment_status(user_id=user_id)

    check_investment_limit(user_id=user_id, amount=amount)

    fund = Fund.objects.get(id=fund_id)
    if not fund.is_active:
        raise FundNotActiveError()
    if amount < fund.minimum_investment:
        raise BelowMinimumInvestmentError(str(fund.minimum_investment))

    nav = get_latest_fund_nav(fund_id=fund_id)
    if nav is None:
        raise NoNAVDataError()

    units = amount / nav.nav_value

    investment = Investment.objects.create(
        user_id=user_id,
        fund_id=fund_id,
        amount=amount,
        units=units,
        nav_at_purchase=nav.nav_value,
        status=status,
        idempotency_key=idempotency_key,
    )

    create_audit_log(
        action=AuditAction.INVESTMENT_CREATED,
        actor_id=user_id,
        entity_type="Investment",
        entity_id=investment.id,
        new_values={"amount": str(amount), "fund_id": str(fund_id)},
    )

    return investment
