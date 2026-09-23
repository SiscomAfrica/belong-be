from __future__ import annotations

from typing import Any

from apps.common.exceptions import ValidationError
from apps.kyc.services.personal_info_checks import checks


def is_absent(value: Any) -> bool:
    """Nothing was supplied for this field.

    The input schema defaults every field, so a value the client never filled
    in arrives as "" or None rather than being missing from the payload. In
    partial mode that is the only signal there is, which also means a field
    cannot be cleared by sending it empty — nothing in the flow does.
    """
    return value is None or (isinstance(value, str) and not value.strip())


def validate_personal_info(
    *, data: dict[str, Any], document_type: str, partial: bool = False,
) -> dict[str, Any]:
    """Validate and normalise a personal-info payload.

    Every field is checked before anything raises, and the problems come back
    together in `details` keyed by field name. One round-trip tells the app
    exactly which inputs to mark — fixing one field at a time, discovering the
    next failure on each submit, is what makes a KYC form feel punitive.

    `partial` is what lets the form be filled across several screens. The KYC
    flow spans three, and each can only save what it collected; requiring the
    whole payload on every save meant screen 2 had to resend screen 1's
    answers, and blanked them whenever it did not have them. In partial mode
    an unsupplied field is skipped entirely — neither validated nor returned,
    so the caller writes nothing over it.

    Absent is not the same as wrong. A value that *is* supplied is always
    checked, in either mode, so nothing invalid reaches the database.
    Completeness is a separate question, asked once at submission.
    """
    cleaned: dict[str, Any] = {}
    problems: dict[str, str] = {}

    for field, check in checks(document_type=document_type).items():
        value = data.get(field)
        if partial and is_absent(value):
            continue
        try:
            cleaned[field] = check(value)
        except ValidationError as exc:
            problems[field] = str(exc)

    if problems:
        raise ValidationError(
            "Some details need fixing.", details={"fields": problems},
        )

    return cleaned
