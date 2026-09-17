from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.investments.models import Holding, InvestmentStatus
from apps.investments.services.execute_recurring_plan import execute_recurring_plan
from apps.payments.models import StandingOrder, StandingOrderStatus
from apps.payments.services.process_c2b_confirmation import process_c2b_confirmation
from apps.payments.services.process_ratiba_callback import process_ratiba_callback
from apps.payments.tests.helpers import balance
from apps.payments.tests.ratiba_payloads import creation

pytestmark = pytest.mark.django_db

REFERENCE = "BLE2ETEST01"


@pytest.fixture
def pending_order(verified_user, plan) -> StandingOrder:
    return StandingOrder.objects.create(
        user=verified_user,
        recurring_plan=plan,
        account_reference=REFERENCE,
        standing_order_name=f"Belong {REFERENCE}",
        amount=plan.amount,
        frequency=plan.frequency,
        start_date=timezone.localdate(),
        end_date=timezone.localdate() + timedelta(days=365),
        phone_number=verified_user.phone,
        status=StandingOrderStatus.PENDING,
    )


def test_the_whole_ratiba_journey(verified_user, plan, pending_order) -> None:
    """Create, approve, collect, invest — the path Safaricom actually drives.

    The two callbacks arrive on different URLs and mean different things, and
    the point of this test is that only one of them is money.
    """
    # 1. The customer approves the M-PESA prompt. The order goes live, but
    #    Safaricom has taken nothing yet.
    process_ratiba_callback(
        payload=creation(ref=str(pending_order.custom_sto_id))
    )

    pending_order.refresh_from_db()
    assert pending_order.status == StandingOrderStatus.ACTIVE
    assert balance(verified_user.id) == Decimal("0.00")

    # 2. Nothing to invest yet, and no STK prompt either: a live standing
    #    order means Safaricom is collecting, so prompting would double-charge.
    assert execute_recurring_plan(plan=plan) is False

    # 3. The execution lands on the paybill as C2B, quoting our reference.
    process_c2b_confirmation(
        payload={
            "TransID": "RKTQDM7W6S",
            "TransAmount": "500",
            "BillRefNumber": REFERENCE,
            "MSISDN": "25470****149",
            "BusinessShortCode": "4148853",
        }
    )
    assert balance(verified_user.id) == Decimal("500.00")

    # 4. The next sweep turns that balance into units.
    assert execute_recurring_plan(plan=plan) is True

    assert balance(verified_user.id) == Decimal("0.00")
    holding = Holding.objects.get(user_id=verified_user.id, fund_id=plan.fund_id)
    assert holding.total_invested == Decimal("500.00")

    plan.refresh_from_db()
    assert plan.is_active is True
    assert plan.next_run_date > timezone.localdate()


def test_investments_from_a_ratiba_contribution_are_confirmed(
    verified_user, plan, pending_order,
) -> None:
    from apps.investments.models import Investment

    process_ratiba_callback(payload=creation(ref=str(pending_order.custom_sto_id)))
    process_c2b_confirmation(
        payload={
            "TransID": "RKTQDM7W6S",
            "TransAmount": "500",
            "BillRefNumber": REFERENCE,
        }
    )
    execute_recurring_plan(plan=plan)

    assert Investment.objects.get().status == InvestmentStatus.CONFIRMED
