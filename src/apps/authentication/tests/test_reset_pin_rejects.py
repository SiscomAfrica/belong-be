from __future__ import annotations

import pytest

from apps.authentication.models import OTP
from apps.authentication.services.consume_reset_otp import (
    MAX_OTP_ATTEMPTS,
    RESET_WINDOW_MINUTES,
)
from apps.authentication.services.reset_pin import reset_pin
from apps.authentication.tests.conftest import CODE, PHONE
from apps.common.exceptions import (
    AuthenticationError,
    OTPExpiredError,
    OTPMaxAttemptsError,
    ValidationError,
)

pytestmark = pytest.mark.django_db


def test_wrong_code_is_rejected_and_counts_an_attempt(user, make_otp) -> None:
    otp = make_otp()

    with pytest.raises(ValidationError):
        reset_pin(phone=PHONE, otp_code="000000", pin="4321")

    otp.refresh_from_db()
    assert otp.attempts == 1


def test_guessing_is_capped(user, make_otp) -> None:
    make_otp()

    for _ in range(MAX_OTP_ATTEMPTS):
        with pytest.raises(ValidationError):
            reset_pin(phone=PHONE, otp_code="000000", pin="4321")

    with pytest.raises(OTPMaxAttemptsError):
        reset_pin(phone=PHONE, otp_code=CODE, pin="4321")


def test_code_older_than_the_window_is_rejected(user, make_otp) -> None:
    make_otp(age_minutes=RESET_WINDOW_MINUTES + 1)

    with pytest.raises(OTPExpiredError):
        reset_pin(phone=PHONE, otp_code=CODE, pin="4321")


def test_a_register_code_cannot_reset_a_pin(user, make_otp) -> None:
    """Only codes issued for signing in or resetting count as reset proof."""
    make_otp(purpose="REGISTER")

    with pytest.raises(OTPExpiredError):
        reset_pin(phone=PHONE, otp_code=CODE, pin="4321")


def test_unknown_phone_does_not_reveal_whether_an_account_exists() -> None:
    with pytest.raises(AuthenticationError):
        reset_pin(phone="+254799999999", otp_code=CODE, pin="4321")

    assert not OTP.objects.exists()
