from __future__ import annotations

from decimal import Decimal

import pytest

from apps.payments.models import WithdrawalStatus
from apps.payments.services.create_withdrawal_request import create_withdrawal_request
from apps.payments.services.process_withdrawal import process_withdrawal
from apps.payments.tests.helpers import balance

pytestmark = pytest.mark.django_db


def test_rejecting_returns_the_funds(funded_user, admin) -> None:
    withdrawal = create_withdrawal_request(
        user_id=funded_user.id, amount=Decimal("400.00"), phone_number="+254700000001",
    )

    process_withdrawal(
        withdrawal_id=withdrawal.id, action="reject", admin_user_id=admin.id,
    )

    assert balance(funded_user.id) == Decimal("1000.00")


def test_rejecting_twice_only_refunds_once(funded_user, admin) -> None:
    withdrawal = create_withdrawal_request(
        user_id=funded_user.id, amount=Decimal("400.00"), phone_number="+254700000001",
    )

    process_withdrawal(
        withdrawal_id=withdrawal.id, action="reject", admin_user_id=admin.id,
    )
    process_withdrawal(
        withdrawal_id=withdrawal.id, action="reject", admin_user_id=admin.id,
    )

    assert balance(funded_user.id) == Decimal("1000.00")


def test_approving_moves_no_money(funded_user, admin) -> None:
    """Funds left the balance at request time; approval must not debit again."""
    withdrawal = create_withdrawal_request(
        user_id=funded_user.id, amount=Decimal("400.00"), phone_number="+254700000001",
    )

    process_withdrawal(
        withdrawal_id=withdrawal.id, action="approve", admin_user_id=admin.id,
    )

    assert balance(funded_user.id) == Decimal("600.00")


def test_processing_after_approval_moves_no_money(funded_user, admin) -> None:
    withdrawal = create_withdrawal_request(
        user_id=funded_user.id, amount=Decimal("400.00"), phone_number="+254700000001",
    )
    process_withdrawal(
        withdrawal_id=withdrawal.id, action="approve", admin_user_id=admin.id,
    )
    result = process_withdrawal(
        withdrawal_id=withdrawal.id, action="process", admin_user_id=admin.id,
    )

    assert result.status == WithdrawalStatus.PROCESSED
    assert balance(funded_user.id) == Decimal("600.00")


def test_rejecting_after_approval_still_refunds(funded_user, admin) -> None:
    withdrawal = create_withdrawal_request(
        user_id=funded_user.id, amount=Decimal("400.00"), phone_number="+254700000001",
    )
    process_withdrawal(
        withdrawal_id=withdrawal.id, action="approve", admin_user_id=admin.id,
    )
    process_withdrawal(
        withdrawal_id=withdrawal.id, action="reject", admin_user_id=admin.id,
    )

    assert balance(funded_user.id) == Decimal("1000.00")


def test_unknown_action_is_rejected(funded_user, admin) -> None:
    withdrawal = create_withdrawal_request(
        user_id=funded_user.id, amount=Decimal("400.00"), phone_number="+254700000001",
    )

    with pytest.raises(ValueError, match="Invalid action"):
        process_withdrawal(
            withdrawal_id=withdrawal.id, action="explode", admin_user_id=admin.id,
        )
