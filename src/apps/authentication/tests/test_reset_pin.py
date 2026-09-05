from __future__ import annotations

import pytest

from apps.authentication.services.login import login
from apps.authentication.services.reset_pin import reset_pin
from apps.authentication.tests.conftest import CODE, PHONE
from apps.common.exceptions import OTPExpiredError, ValidationError

pytestmark = pytest.mark.django_db


def test_reset_accepts_a_code_the_client_already_verified(user, make_otp) -> None:
    """The app verifies on its own screen, so the code arrives here spent."""
    make_otp()

    reset_pin(phone=PHONE, otp_code=CODE, pin="4321")

    assert login(phone=PHONE, pin="4321")["access"]


def test_reset_consumes_the_code_so_it_cannot_be_replayed(user, make_otp) -> None:
    make_otp()
    reset_pin(phone=PHONE, otp_code=CODE, pin="4321")

    with pytest.raises(OTPExpiredError):
        reset_pin(phone=PHONE, otp_code=CODE, pin="9999")


def test_invalid_pin_leaves_the_code_usable_for_a_retry(user, make_otp) -> None:
    """A rejected PIN must not cost the user another SMS."""
    make_otp()

    with pytest.raises(ValidationError):
        reset_pin(phone=PHONE, otp_code=CODE, pin="12")

    reset_pin(phone=PHONE, otp_code=CODE, pin="4321")
    assert login(phone=PHONE, pin="4321")["access"]


def test_a_reset_pin_purpose_code_is_also_accepted(user, make_otp) -> None:
    """So the client can move to the purpose that names the operation."""
    make_otp(purpose="RESET_PIN")

    reset_pin(phone=PHONE, otp_code=CODE, pin="4321")

    assert login(phone=PHONE, pin="4321")["access"]
