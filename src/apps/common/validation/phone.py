from __future__ import annotations

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat, PhoneNumberType

from apps.common.exceptions import ValidationError
from apps.common.validation.text import sanitise_identifier

DEFAULT_REGION = "KE"

# Belong reaches a customer's number two ways: an OTP over SMS and an M-Pesa
# STK push. Both require a mobile line, so a valid landline is still useless
# here — +254 20 xxx xxxx parses and validates, and would then silently never
# receive a prompt. FIXED_LINE_OR_MOBILE is allowed because some ranges are
# genuinely ambiguous in the metadata and rejecting them would lock out real
# subscribers.
_ACCEPTED_TYPES = frozenset(
    {
        PhoneNumberType.MOBILE,
        PhoneNumberType.FIXED_LINE_OR_MOBILE,
    },
)


def validate_mobile_e164(*, value: str, field: str = "phone") -> str:
    """Return a mobile number in E.164, or raise.

    Parsed with an explicit default region rather than requiring a '+', so a
    customer may type 0712345678 as they would anywhere else. The stored form
    is always E.164 — one representation per subscriber, so a number cannot be
    registered twice in two different shapes.
    """
    cleaned = sanitise_identifier(value=value, field=field, max_length=24)
    if not cleaned:
        raise ValidationError(f"{field} is required.")

    try:
        parsed = phonenumbers.parse(cleaned, DEFAULT_REGION)
    except NumberParseException:
        raise ValidationError(f"{field} is not a valid phone number.") from None

    if not phonenumbers.is_valid_number(parsed):
        raise ValidationError(f"{field} is not a valid phone number.")

    if phonenumbers.number_type(parsed) not in _ACCEPTED_TYPES:
        raise ValidationError(
            f"{field} must be a mobile number — we send an SMS code and an "
            "M-Pesa prompt to it.",
        )

    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
