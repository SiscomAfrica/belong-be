from __future__ import annotations

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.funds.models import Fund
from apps.investments.models.recurring_plan import PlanFrequency, RecurringPlan
from apps.users.models import User


@pytest.fixture
def user() -> User:
    return User.objects.create(
        phone="+254700000021", username="saver", referral_code="SAVER001",
    )


@pytest.fixture
def fund() -> Fund:
    return Fund.objects.create(
        name="Stable Gains",
        slug="stable-gains",
        description="Test fund.",
        fund_type="ETF",
        category="DIVIDEND",
        risk_level=2,
        currency="KES",
        minimum_investment=Decimal("100.00"),
        projected_annual_return=Decimal("10.00"),
        effective_annual_yield=Decimal("10.00"),
        annualized_daily_yield=Decimal("0.03"),
    )


@pytest.fixture
def plan(user: User, fund: Fund) -> RecurringPlan:
    """A plan due today, as the beat job would find it."""
    return RecurringPlan.objects.create(
        user=user,
        fund=fund,
        amount=Decimal("500.00"),
        frequency=PlanFrequency.MONTHLY,
        next_run_date=timezone.localdate(),
    )


@pytest.fixture
def verified_user(user: User) -> User:
    """A user past KYC, so investments confirm rather than parking."""
    from apps.kyc.models import KYCStatus, KYCSubmission

    KYCSubmission.objects.create(user=user, status=KYCStatus.VERIFIED)
    return user


@pytest.fixture
def standing_order(user: User, plan: RecurringPlan):
    """A live Ratiba order, so the plan is already being collected against."""
    from datetime import timedelta

    from apps.payments.models import StandingOrder, StandingOrderStatus

    return StandingOrder.objects.create(
        user=user,
        recurring_plan=plan,
        account_reference="BLPLANREF01",
        standing_order_name="Belong BLPLANREF01",
        response_ref_id="plan-ref-1",
        amount=plan.amount,
        frequency=plan.frequency,
        start_date=timezone.localdate(),
        end_date=timezone.localdate() + timedelta(days=365),
        phone_number=user.phone,
        status=StandingOrderStatus.ACTIVE,
    )
