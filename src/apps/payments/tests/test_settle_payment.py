from __future__ import annotations

from decimal import Decimal

import pytest

from apps.investments.models import Investment, InvestmentStatus
from apps.payments.models import PaymentStatus
from apps.payments.services.settle_payment import (
    settle_failed_payment,
    settle_successful_payment,
)
from apps.payments.tests.helpers import balance

pytestmark = pytest.mark.django_db


def test_investment_payment_does_not_credit_the_wallet(
    user, investment, make_payment,
) -> None:
    """The double count: cash spent on units must not also appear as cash."""
    txn = make_payment(investment=investment)

    settle_successful_payment(txn=txn)

    investment.refresh_from_db()
    assert investment.status == InvestmentStatus.CONFIRMED
    assert balance(user.id) == Decimal("0.00")


def test_topup_payment_credits_the_wallet(user, make_payment) -> None:
    """A payment with no investment is a top-up and is the wallet's only inflow."""
    txn = make_payment(investment=None, amount="500.00")

    settle_successful_payment(txn=txn)

    assert balance(user.id) == Decimal("500.00")


def test_investment_awaiting_kyc_is_not_confirmed_yet(
    user, investment, make_payment,
) -> None:
    investment.status = InvestmentStatus.PENDING_KYC
    investment.save(update_fields=["status"])
    txn = make_payment(investment=investment)

    settle_successful_payment(txn=txn)

    investment.refresh_from_db()
    assert investment.status == InvestmentStatus.PENDING_KYC
    assert balance(user.id) == Decimal("0.00")


def test_successful_payment_is_marked_success(user, investment, make_payment) -> None:
    txn = make_payment(investment=investment)

    settle_successful_payment(txn=txn)

    txn.refresh_from_db()
    assert txn.status == PaymentStatus.SUCCESS
    assert txn.completed_at is not None


def test_failed_payment_cancels_the_investment(user, investment, make_payment) -> None:
    txn = make_payment(investment=investment)

    settle_failed_payment(txn=txn, reason="Insufficient funds")

    txn.refresh_from_db()
    investment.refresh_from_db()
    assert txn.status == PaymentStatus.FAILED
    assert txn.failure_reason == "Insufficient funds"
    assert investment.status == InvestmentStatus.CANCELLED
    assert balance(user.id) == Decimal("0.00")


def test_failed_topup_leaves_the_wallet_untouched(user, make_payment) -> None:
    txn = make_payment(investment=None, amount="500.00")

    settle_failed_payment(txn=txn, reason="Cancelled by user")

    assert balance(user.id) == Decimal("0.00")


def test_holdings_and_wallet_do_not_both_reflect_the_same_money(
    user, investment, make_payment,
) -> None:
    """The regression this whole change exists to prevent."""
    txn = make_payment(investment=investment)

    settle_successful_payment(txn=txn)

    from apps.investments.models import Holding

    holding = Holding.objects.get(user_id=user.id, fund_id=investment.fund_id)
    assert holding.total_invested == Decimal("1000.00")
    assert balance(user.id) == Decimal("0.00")

    total_recorded = holding.total_invested + balance(user.id)
    assert total_recorded == Investment.objects.get(id=investment.id).amount
