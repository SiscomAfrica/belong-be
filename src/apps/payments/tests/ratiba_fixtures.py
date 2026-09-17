from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.funds.models import Fund
from apps.users.models import User


@pytest.fixture
def plan(user: User, fund: Fund):
    from apps.investments.models.recurring_plan import PlanFrequency, RecurringPlan

    return RecurringPlan.objects.create(
        user=user,
        fund=fund,
        amount=Decimal("500.00"),
        frequency=PlanFrequency.MONTHLY,
        next_run_date=timezone.localdate(),
    )


@pytest.fixture
def standing_order(user: User, plan):
    """A standing order waiting on the customer's M-PESA PIN approval."""
    from apps.payments.models import StandingOrder, StandingOrderStatus

    return StandingOrder.objects.create(
        user=user,
        recurring_plan=plan,
        account_reference="BLTESTREF01",
        standing_order_name="Belong BLTESTREF01",
        response_ref_id="ref-abc-123",
        amount=Decimal("500.00"),
        frequency="MONTHLY",
        start_date=timezone.localdate(),
        end_date=timezone.localdate() + timedelta(days=365),
        phone_number="+254700000001",
        status=StandingOrderStatus.PENDING,
    )
