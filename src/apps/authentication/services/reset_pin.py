from __future__ import annotations

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.authentication.models import OTP
from apps.authentication.services.consume_reset_otp import consume_reset_otp
from apps.authentication.services.set_pin import set_pin
from apps.common.exceptions import AuthenticationError, OTPExpiredError
from apps.users.models import User
from apps.users.selectors.get_user_by_phone import get_user_by_phone


def reset_pin(*, phone: str, otp_code: str, pin: str) -> User:
    """Set a new PIN for a user who proved ownership of the phone by OTP.

    Unauthenticated by necessity: the caller has forgotten the PIN, so there is
    no session to authenticate with. Possession of a code issued to that phone
    minutes earlier is the whole proof, which is why the code is consumed here
    rather than simply read.
    """
    user = get_user_by_phone(phone=phone)
    if user is None or not user.is_active:
        # One message whichever half failed, so this cannot be used to discover
        # which phone numbers have accounts.
        raise AuthenticationError("Invalid phone number or code.")

    otp = consume_reset_otp(phone=phone, code=otp_code)

    with transaction.atomic():
        # Re-read under a lock before spending it: two requests replaying the
        # same code concurrently must not both get through, and the row's
        # existence is the only thing making the code single-use.
        locked = OTP.objects.select_for_update().filter(pk=otp.pk).first()
        if locked is None:
            raise OTPExpiredError("This code has already been used.")

        # Ordered so an invalid PIN raises before the code is spent, leaving
        # the user able to retry without requesting a new SMS.
        user = set_pin(user=user, pin=pin)
        locked.delete()

    create_audit_log(
        action=AuditAction.PIN_CHANGED,
        actor_id=user.id,
        entity_type="User",
        entity_id=user.id,
        new_values={"method": "OTP_RESET"},
    )

    return user
