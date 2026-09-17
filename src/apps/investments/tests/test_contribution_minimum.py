from __future__ import annotations

from decimal import Decimal

import pytest

from apps.investments.exceptions import BelowMinimumContributionError
from apps.investments.models import Holding, InvestmentSettings
from apps.investments.services.create_recurring_plan import create_recurring_plan
from apps.investments.services.execute_recurring_plan import execute_recurring_plan
from apps.payments.services.credit_wallet import credit_wallet

pytestmark = pytest.mark.django_db


def _set_floor(amount: str) -> None:
    InvestmentSettings.objects.all().delete()
    InvestmentSettings.objects.create(min_contribution=Decimal(amount))


def test_a_contribution_below_the_floor_is_rejected(user, fund) -> None:
    _set_floor("10")

    with pytest.raises(BelowMinimumContributionError):
        create_recurring_plan(
            user_id=user.id,
            fund_id=fund.id,
            amount=Decimal("9"),
            frequency="DAILY",
            phone_number=user.phone,
        )


def test_the_floor_is_configurable(user, fund) -> None:
    """Set to 1 in the admin, end-to-end Ratiba testing costs a shilling."""
    _set_floor("1")

    plan = create_recurring_plan(
        user_id=user.id,
        fund_id=fund.id,
        amount=Decimal("1"),
        frequency="DAILY",
        phone_number=user.phone,
    )

    assert plan.amount == Decimal("1")


def test_a_contribution_may_sit_below_the_fund_s_lump_sum_minimum(
    verified_user, fund, plan,
) -> None:
    """A plan drips in and accumulates, so it is not held to the lump-sum floor.

    The fund's own minimum_investment is 100. A 1 KSh contribution must still
    buy units, or a configurable floor below the fund minimum would be a floor
    that silently fails on every sweep.
    """
    _set_floor("1")
    assert fund.minimum_investment == Decimal("100.00")

    plan.amount = Decimal("1")
    plan.save(update_fields=["amount"])
    credit_wallet(user_id=verified_user.id, amount=Decimal("1"), currency="KES")

    assert execute_recurring_plan(plan=plan) is True

    holding = Holding.objects.get(user_id=verified_user.id, fund_id=plan.fund_id)
    assert holding.total_invested == Decimal("1")


def test_the_default_floor_is_used_when_no_row_exists(user, fund) -> None:
    """A fresh database must not make plan creation blow up."""
    InvestmentSettings.objects.all().delete()

    with pytest.raises(BelowMinimumContributionError):
        create_recurring_plan(
            user_id=user.id,
            fund_id=fund.id,
            amount=Decimal("50"),
            frequency="DAILY",
            phone_number=user.phone,
        )

    assert InvestmentSettings.objects.get().min_contribution == Decimal("100.00")
