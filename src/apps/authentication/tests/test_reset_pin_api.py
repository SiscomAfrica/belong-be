from __future__ import annotations

import pytest

from apps.authentication.tests.conftest import CODE, PHONE

pytestmark = pytest.mark.django_db

RESET = "/auth/pin/reset"
UNPROCESSABLE = 422


def _payload(*, code: str = CODE, pin: str = "4321") -> dict:
    return {"phone": PHONE, "otp_code": code, "pin": pin}


def test_reset_is_reachable_without_a_token(client, user, make_otp) -> None:
    """The caller has forgotten their PIN, so there is no session to send."""
    make_otp()

    response = client.post(RESET, json=_payload())

    assert response.status_code == 200, response.content
    assert response.json()["phone"] == PHONE


def test_response_never_carries_the_pin_hash(client, user, make_otp) -> None:
    make_otp()

    body = client.post(RESET, json=_payload()).json()

    assert "pin_hash" not in body


def test_bad_code_returns_a_coded_error_not_a_stack_trace(client, user, make_otp) -> None:
    make_otp()

    response = client.post(RESET, json=_payload(code="000000"))

    assert response.status_code == UNPROCESSABLE
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_audit_log_records_the_change(client, user, make_otp) -> None:
    from apps.audit.models import AuditAction, AuditLog

    make_otp()
    client.post(RESET, json=_payload())

    entry = AuditLog.objects.filter(action=AuditAction.PIN_CHANGED).get()
    assert entry.actor_id == user.id
    assert entry.new_values == {"method": "OTP_RESET"}
