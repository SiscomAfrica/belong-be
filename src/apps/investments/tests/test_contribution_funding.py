from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

import pytest

from apps.investments.services.execute_recurring_plan import execute_recurring_plan
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.payments.services.credit_wallet import credit_wallet

pytestmark = pytest.mark.django_db

INIT = "apps.payments.services.initiate_wallet_topup.get_provider"


class _StubProvider:
    """Stands in for Safaricom so no test ever reaches the network."""

    def __init__(self) -> None:
        self.calls: list[Decimal] = []

    def __call__(self, _provider: str):
        return self

    def initiate_payment(self, *, amount, phone_number, reference):
        self.calls.append(amount)
        from apps.payments.providers.base import ProviderInitResult

        return ProviderInitResult(external_ref=f"stk-{reference}")


def test_an_unfunded_contribution_asks_for_the_money(user, plan) -> None:
    stub = _StubProvider()
    with patch(INIT, stub):
        assert execute_recurring_plan(plan=plan) is False

    assert stub.calls == [Decimal("500")]
    txn = PaymentTransaction.objects.get()
    assert txn.investment_id is None
    assert txn.status == PaymentStatus.INITIATED


def test_only_the_shortfall_is_requested(user, plan) -> None:
    """A partly funded wallet is topped up to the line, not charged twice."""
    credit_wallet(user_id=user.id, amount=Decimal("300.00"), currency="KES")
    stub = _StubProvider()

    with patch(INIT, stub):
        execute_recurring_plan(plan=plan)

    assert stub.calls == [Decimal("200")]


def test_a_shortfall_is_rounded_up_to_whole_shillings(user, plan) -> None:
    """M-Pesa takes whole numbers; rounding down would leave the plan stuck."""
    credit_wallet(user_id=user.id, amount=Decimal("300.50"), currency="KES")
    stub = _StubProvider()

    with patch(INIT, stub):
        execute_recurring_plan(plan=plan)

    assert stub.calls == [Decimal("200")]


def test_the_customer_is_prompted_once_per_due_date(user, plan) -> None:
    """Seven days unfunded is one prompt, not seven."""
    stub = _StubProvider()
    with patch(INIT, stub):
        execute_recurring_plan(plan=plan)
        execute_recurring_plan(plan=plan)
        execute_recurring_plan(plan=plan)

    assert len(stub.calls) == 1
    assert PaymentTransaction.objects.count() == 1


def test_a_live_standing_order_suppresses_the_prompt(user, plan, standing_order) -> None:
    """Ratiba is already collecting; prompting too would take it twice."""
    stub = _StubProvider()
    with patch(INIT, stub):
        assert execute_recurring_plan(plan=plan) is False

    assert stub.calls == []
    assert PaymentTransaction.objects.count() == 0


def test_a_funded_plan_is_never_prompted(verified_user, plan) -> None:
    credit_wallet(user_id=verified_user.id, amount=Decimal("500.00"), currency="KES")
    stub = _StubProvider()

    with patch(INIT, stub):
        assert execute_recurring_plan(plan=plan) is True

    assert stub.calls == []
