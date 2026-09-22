from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoError
from django.core.validators import validate_email as django_validate_email

from apps.common.exceptions import ValidationError
from apps.common.validation.text import sanitise_text


def validate_email(*, value: str, field: str = "email") -> str:
    """Validate an address with Django's validator rather than a regex.

    A hand-rolled email pattern is either wrong or unreadable. Django's is
    already here, so this needs no new dependency — Pydantic's EmailStr would
    pull in email-validator for the same result.
    """
    cleaned = sanitise_text(value=value, field=field, max_length=254).lower()
    if not cleaned:
        raise ValidationError(f"{field} is required.")

    # Stripping the space out of "a b@c.com" would accept a typo and then
    # deliver to an address the user never typed. Reject it instead.
    if " " in cleaned:
        raise ValidationError(f"{field} cannot contain spaces.")

    try:
        django_validate_email(cleaned)
    except DjangoError:
        raise ValidationError(f"{field} is not a valid email address.") from None

    return cleaned
