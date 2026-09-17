from __future__ import annotations

from decimal import Decimal

import pytest

from apps.investments.models import Holding, Investment, InvestmentStatus
from apps.investments.models.recurring_plan import PlanFrequency
from apps.investments.services.execute_recurring_plan import execute_recurring_plan
from apps.payments.services.credit_wallet import credit_wallet
from apps.payments.tests.helpers import balance

pytestmark = pytest.mark.django_db


def _fund_wallet(user, amount: str = "500.00") -> None:
    credit_wallet(user_id=user.id, amount=Decimal(amount), currency="KES")


def test_a_funded_plan_moves_the_money_from_wallet_to_fund(verified_user, plan) -> None:
    _fund_wallet(verified_user)

    assert execute_recurring_plan(plan=plan) is True

    assert balance(verified_user.id) == Decimal("0.00")
    holding = Holding.objects.get(user_id=verified_user.id, fund_id=plan.fund_id)
    assert holding.total_invested == Decimal("500.00")


def test_an_unfunded_plan_invests_nothing_and_keeps_its_due_date(
    verified_user, plan,
) -> None:
    """Ratiba collects on Safaricom's clock; a late deduction is not a failure."""
    due = plan.next_run_date

    assert execute_recurring_plan(plan=plan) is False

    plan.refresh_from_db()
    assert plan.next_run_date == due
    assert plan.is_active is True
    assert Investment.objects.count() == 0


def test_a_short_wallet_is_not_partially_invested(verified_user, plan) -> None:
    _fund_wallet(verified_user, "499.00")

    assert execute_recurring_plan(plan=plan) is False

    assert balance(verified_user.id) == Decimal("499.00")


def test_a_successful_run_advances_to_the_next_contribution(verified_user, plan) -> None:
    _fund_wallet(verified_user)
    due = plan.next_run_date

    execute_recurring_plan(plan=plan)

    plan.refresh_from_db()
    assert plan.next_run_date > due


def test_a_one_off_plan_retires_after_it_runs(verified_user, plan) -> None:
    plan.frequency = PlanFrequency.ONE_OFF
    plan.save(update_fields=["frequency"])
    _fund_wallet(verified_user)

    execute_recurring_plan(plan=plan)

    plan.refresh_from_db()
    assert plan.is_active is False


def test_an_unverified_user_is_debited_but_not_credited_units(user, plan) -> None:
    """The KYC gate holds: cash is taken, units wait for activation."""
    _fund_wallet(user)

    assert execute_recurring_plan(plan=plan) is True

    investment = Investment.objects.get()
    assert investment.status == InvestmentStatus.PENDING_KYC
    assert not Holding.objects.filter(user_id=user.id).exists()
    assert balance(user.id) == Decimal("0.00")


def test_replaying_a_due_date_does_not_debit_the_wallet_twice(
    verified_user, plan,
) -> None:
    """A run that invested but died before advancing must not re-charge."""
    _fund_wallet(verified_user, "1000.00")
    due = plan.next_run_date

    execute_recurring_plan(plan=plan)
    plan.next_run_date = due
    plan.save(update_fields=["next_run_date"])
    execute_recurring_plan(plan=plan)

    assert Investment.objects.count() == 1
    # 1000 in, exactly one 500 contribution taken.
    assert balance(verified_user.id) == Decimal("500.00")
