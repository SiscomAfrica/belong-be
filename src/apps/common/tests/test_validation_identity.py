from __future__ import annotations

import pytest

from apps.common.exceptions import ValidationError
from apps.common.validation import (
    validate_country_code,
    validate_document_number,
    validate_kra_pin,
    validate_mobile_e164,
    validate_pin,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0712345678", "+254712345678"),
        ("+254712345678", "+254712345678"),
        ("254 712 345 678", "+254712345678"),
        ("+254 (712) 345-678", "+254712345678"),
    ],
)
def test_mobile_numbers_normalise_to_one_stored_form(raw: str, expected: str) -> None:
    """One representation per subscriber, or the same person registers twice."""
    assert validate_mobile_e164(value=raw) == expected


def test_a_valid_landline_is_still_rejected() -> None:
    """+254 20 is a real Nairobi number that parses and validates — and would
    then silently never receive an OTP or an M-Pesa prompt.
    """
    with pytest.raises(ValidationError, match="mobile number"):
        validate_mobile_e164(value="+254201234567")


@pytest.mark.parametrize(
    ("number", "document_type", "ok"),
    [
        ("12345678", "NATIONAL_ID", True),
        ("1234567", "NATIONAL_ID", True),
        ("123456", "NATIONAL_ID", False),
        ("AK1234567", "NATIONAL_ID", False),
        ("AK1234567", "PASSPORT", True),
        ("12345678", "PASSPORT", False),
    ],
)
def test_id_number_is_checked_against_its_own_document_type(
    number: str, document_type: str, ok: bool,
) -> None:
    """One rule cannot serve all three — validating every document as a
    national ID would reject every passport holder on the platform.
    """
    if ok:
        assert validate_document_number(
            value=number, document_type=document_type,
        ) == number
    else:
        with pytest.raises(ValidationError):
            validate_document_number(value=number, document_type=document_type)


def test_a_company_kra_pin_is_rejected_with_a_specific_message() -> None:
    """Filing an individual's holdings under a P PIN files them against a
    company's tax identity.
    """
    with pytest.raises(ValidationError, match="non-individual"):
        validate_kra_pin(value="P012345678Z")


def test_kra_pin_is_optional_but_never_malformed() -> None:
    assert validate_kra_pin(value="") == ""
    assert validate_kra_pin(value="a012345678z") == "A012345678Z"
    with pytest.raises(ValidationError):
        validate_kra_pin(value="A12345Z")


def test_alpha_three_country_codes_are_normalised_not_rejected() -> None:
    assert validate_country_code(value="KEN") == "KE"
    assert validate_country_code(value="ke") == "KE"


def test_an_oversized_pin_is_rejected_before_bcrypt_sees_it() -> None:
    """bcrypt is deliberately slow, so an unbounded PIN on an unauthenticated
    endpoint is free CPU for an attacker to burn.
    """
    with pytest.raises(ValidationError):
        validate_pin(value="1" * 5000)
