from __future__ import annotations

from datetime import date

import pytest

from apps.common.exceptions import ValidationError
from apps.kyc.services.validate_personal_info import validate_personal_info

VALID = {
    "first_name": "Wanjiku",
    "last_name": "Otieno",
    "date_of_birth": date(1995, 4, 12),
    "nationality": "ke",
    "id_number": "12345678",
    "kra_pin": "A012345678Z",
    "city": "Nairobi",
    "address": "12 Kenyatta Avenue",
    "employment_status": "employed",
    "income_source": "salary",
    "kin_name": "Grace Otieno",
    "kin_phone": "0722123456",
    "kin_email": "Grace@Example.com",
}


def test_a_build_already_in_users_hands_still_passes() -> None:
    """Shipped builds send lower-cased picker ids and a local phone number.
    Rejecting those breaks KYC for everyone until they update — and an app
    release cannot be forced.
    """
    cleaned = validate_personal_info(data=VALID, document_type="NATIONAL_ID")

    assert cleaned["employment_status"] == "EMPLOYED"
    assert cleaned["income_source"] == "SALARY"
    assert cleaned["nationality"] == "KE"
    assert cleaned["kin_phone"] == "+254722123456"
    assert cleaned["kin_email"] == "grace@example.com"


def test_legacy_other_nationality_is_stored_empty_not_rejected() -> None:
    """Shipped builds offer four nationalities, the last being "other". That
    is not a country code and cannot be stored as one, but blocking those
    users mid-KYC over it is worse than leaving the field for a reviewer.
    """
    cleaned = validate_personal_info(
        data={**VALID, "nationality": "other"}, document_type="NATIONAL_ID",
    )

    assert cleaned["nationality"] == ""


def test_every_problem_is_reported_in_one_response() -> None:
    """Fixing one field per submit is what makes a KYC form feel punitive."""
    with pytest.raises(ValidationError) as caught:
        validate_personal_info(
            data={
                **VALID,
                "first_name": "R'); DROP TABLE users;--",
                "last_name": "",
                "date_of_birth": date(2015, 1, 1),
                "city": "",
                "kin_email": "not-an-email",
            },
            document_type="NATIONAL_ID",
        )

    fields = caught.value.details["fields"]

    assert set(fields) == {
        "first_name", "last_name", "date_of_birth", "city", "kin_email",
    }


def test_id_number_follows_the_submissions_document_type() -> None:
    passport = validate_personal_info(
        data={**VALID, "id_number": "AK1234567"}, document_type="PASSPORT",
    )
    assert passport["id_number"] == "AK1234567"

    with pytest.raises(ValidationError) as caught:
        validate_personal_info(data=VALID, document_type="PASSPORT")
    assert "id_number" in caught.value.details["fields"]


def test_next_of_kin_details_stay_optional() -> None:
    cleaned = validate_personal_info(
        data={**VALID, "kin_name": "", "kin_phone": "", "kin_email": ""},
        document_type="NATIONAL_ID",
    )

    assert cleaned["kin_name"] == ""
    assert cleaned["kin_phone"] == ""
