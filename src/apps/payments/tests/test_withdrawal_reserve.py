from __future__ import annotations

from decimal import Decimal

import pytest

from apps.payments.exceptions import InsufficientBalanceError
from apps.payments.services.create_withdrawal_request import create_withdrawal_request
from apps.payments.tests.helpers import balance

pytestmark = pytest.mark.django_db


def test_requesting_a_withdrawal_reserves_the_funds(funded_user) -> None:
    create_withdrawal_request(
        user_id=funded_user.id, amount=Decimal("400.00"), phone_number="+254700000001",
    )

    assert balance(funded_user.id) == Decimal("600.00")


def test_cannot_withdraw_more_than_the_balance(funded_user) -> None:
    with pytest.raises(InsufficientBalanceError):
        create_withdrawal_request(
            user_id=funded_user.id,
            amount=Decimal("1500.00"),
            phone_number="+254700000001",
        )

    assert balance(funded_user.id) == Decimal("1000.00")


def test_queued_withdrawals_cannot_overdraw_in_aggregate(funded_user) -> None:
    """Each request passes on its own; only reserving up front stops the overdraw."""
    create_withdrawal_request(
        user_id=funded_user.id, amount=Decimal("600.00"), phone_number="+254700000001",
    )

    with pytest.raises(InsufficientBalanceError):
        create_withdrawal_request(
            user_id=funded_user.id,
            amount=Decimal("600.00"),
            phone_number="+254700000001",
        )

    assert balance(funded_user.id) == Decimal("400.00")
