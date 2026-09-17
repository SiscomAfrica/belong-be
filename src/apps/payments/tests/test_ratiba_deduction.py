from __future__ import annotations

from decimal import Decimal

import pytest

from apps.payments.models import ChargeKind, StandingOrderCharge, StandingOrderStatus
from apps.payments.services.process_ratiba_callback import process_ratiba_callback
from apps.payments.tests.helpers import balance
from apps.payments.tests.ratiba_payloads import creation, execution

pytestmark = pytest.mark.django_db


def test_setting_up_a_standing_order_credits_nothing(user, standing_order) -> None:
    """The creation callback carries an Amount but no money has moved."""
    process_ratiba_callback(payload=creation(ref=str(standing_order.custom_sto_id)))

    assert balance(user.id) == Decimal("0.00")
    assert StandingOrderCharge.objects.get().kind == ChargeKind.ACTIVATION


def test_setting_up_a_standing_order_activates_it(standing_order) -> None:
    process_ratiba_callback(payload=creation(ref=str(standing_order.custom_sto_id)))

    standing_order.refresh_from_db()
    assert standing_order.status == StandingOrderStatus.ACTIVE
    assert standing_order.reminder_schedule_id == "2571168"
    assert standing_order.first_execution_date.isoformat() == "2026-08-07"


def test_a_deduction_credits_the_wallet(user, standing_order) -> None:
    ref = str(standing_order.custom_sto_id)
    process_ratiba_callback(payload=creation(ref=ref))

    process_ratiba_callback(payload=execution(ref=ref))

    assert balance(user.id) == Decimal("500.00")
    assert StandingOrderCharge.objects.filter(kind=ChargeKind.DEDUCTION).count() == 1


def test_a_replayed_creation_callback_is_not_read_as_a_deduction(
    user, standing_order,
) -> None:
    """The order is ACTIVE by the retry, so only the id keeps it honest."""
    payload = creation(ref=str(standing_order.custom_sto_id))

    process_ratiba_callback(payload=payload)
    process_ratiba_callback(payload=payload)

    assert balance(user.id) == Decimal("0.00")
    assert StandingOrderCharge.objects.count() == 1


def test_a_declined_prompt_fails_the_standing_order(user, standing_order) -> None:
    process_ratiba_callback(
        payload=creation(ref=str(standing_order.custom_sto_id), ok=False)
    )

    standing_order.refresh_from_db()
    assert standing_order.status == StandingOrderStatus.FAILED
    assert "1032" in standing_order.failure_reason
    assert balance(user.id) == Decimal("0.00")
