from __future__ import annotations

import re

from apps.common.exceptions import ValidationError
from apps.common.validation.text import sanitise_identifier

# Kenyan document formats. Each is deliberately a shape check and nothing
# more: none of these numbers carries a published checksum, so the only real
# verification is a human comparing the number against the uploaded image.
# The point of these patterns is to stop a typo reaching a reviewer, not to
# prove the document exists.

# National ID: 7 or 8 digits. Older cards are 7; anything issued in recent
# years is 8. Leading zeros are significant, which is why this is stored as
# text and never as an integer.
NATIONAL_ID = re.compile(r"^\d{7,8}$")

# Kenyan passports: one or two letters then six to eight digits (older books
# are A1234567, the current series AK1234567).
PASSPORT = re.compile(r"^[A-Z]{1,2}\d{6,8}$")

# Driving licence numbers are not standardised to a single published format,
# so this stays deliberately loose — alphanumeric, plausible length.
DRIVING_LICENSE = re.compile(r"^[A-Z0-9]{6,15}$")

# KRA PIN: a prefix letter, nine digits, then a check letter — A012345678Z.
# 'A' is an individual and 'P' a non-individual; a personal KYC submission
# should never carry a P PIN, and accepting one would file an individual's
# holdings under a company's tax identity.
KRA_PIN = re.compile(r"^A\d{9}[A-Z]$")

_DOCUMENT_RULES = {
    "NATIONAL_ID": (NATIONAL_ID, "7 or 8 digits"),
    "PASSPORT": (PASSPORT, "one or two letters followed by 6-8 digits"),
    "DRIVING_LICENSE": (DRIVING_LICENSE, "6-15 letters or digits"),
}


def validate_document_number(
    *, value: str, document_type: str, field: str = "id_number",
) -> str:
    """Check an ID number against the format its own document type uses.

    One rule cannot serve all three: a passport number is not eight digits,
    and validating every document as a national ID would reject every
    passport holder on the platform.
    """
    cleaned = sanitise_identifier(value=value, field=field, max_length=20)
    if not cleaned:
        raise ValidationError(f"{field} is required.")

    rule = _DOCUMENT_RULES.get(document_type)
    if rule is None:
        raise ValidationError(f"Unknown document type {document_type!r}.")

    pattern, expected = rule
    if not pattern.match(cleaned):
        raise ValidationError(
            f"{field} does not look like a {document_type.replace('_', ' ').lower()} "
            f"number — expected {expected}.",
        )

    return cleaned


def validate_kra_pin(*, value: str, field: str = "kra_pin") -> str:
    """Check a personal KRA PIN. Empty is allowed; malformed is not."""
    cleaned = sanitise_identifier(value=value, field=field, max_length=11)
    if not cleaned:
        return ""

    if KRA_PIN.match(cleaned):
        return cleaned

    if cleaned.startswith("P"):
        raise ValidationError(
            f"{field} is a non-individual PIN. Use the personal PIN that "
            "starts with A.",
        )

    raise ValidationError(
        f"{field} must look like A012345678Z — an A, nine digits, then a letter.",
    )
