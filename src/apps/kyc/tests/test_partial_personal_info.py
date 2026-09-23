from __future__ import annotations

from datetime import date

import pytest

from apps.common.exceptions import ValidationError
from apps.kyc.models import KYCStatus, KYCSubmission
from apps.kyc.services.save_personal_info import save_personal_info
from apps.kyc.services.start_kyc import start_kyc
from apps.kyc.services.submit_for_review import submit_for_review
from apps.users.models import User

pytestmark = pytest.mark.django_db

SCREEN_ONE = {
    "first_name": "Wanjiku",
    "last_name": "Otieno",
    "date_of_birth": date(1995, 4, 12),
    "nationality": "ke",
    "id_number": "12345678",
    "kra_pin": "A012345678Z",
}

SCREEN_TWO = {
    "city": "Nairobi",
    "address": "12 Kenyatta Avenue",
    "employment_status": "employed",
    "income_source": "salary",
}


@pytest.fixture
def user() -> User:
    """A user who has begun KYC, as every caller of save_personal_info has.

    start_kyc is what puts document_type on the submission, and the ID number
    check reads it — validation of id_number is meaningless without it.
    """
    created = User.objects.create(
        phone="+254700000009", username="kycu", referral_code="KYCUSER01",
    )
    start_kyc(user_id=created.id, document_type="NATIONAL_ID")
    return created


def test_screen_one_saves_on_its_own(user: User) -> None:
    """The whole point: a screen can store what it collected without being
    able to answer for the screens after it.
    """
    submission = save_personal_info(user_id=user.id, **SCREEN_ONE)

    assert submission.id_number == "12345678"
    assert submission.city == ""


def test_screen_two_does_not_blank_screen_one(user: User) -> None:
    """The bug this exists to prevent. Screen 2 has no inputs for the ID
    number or date of birth, so it sends nothing for them — which used to be
    written as empty over answers the server already held.
    """
    save_personal_info(user_id=user.id, **SCREEN_ONE)
    submission = save_personal_info(user_id=user.id, **SCREEN_TWO)

    assert submission.id_number == "12345678"
    assert submission.date_of_birth == date(1995, 4, 12)
    assert submission.city == "Nairobi"


def test_a_supplied_value_is_still_checked(user: User) -> None:
    """Absent is not the same as wrong: skipping empties must not become a
    way to smuggle a malformed value past validation.
    """
    with pytest.raises(ValidationError) as caught:
        save_personal_info(user_id=user.id, kra_pin="not-a-pin")

    assert "kra_pin" in caught.value.details["fields"]


def test_an_incomplete_record_cannot_be_submitted(user: User) -> None:
    """Partial saving is fine right up until a reviewer is asked to act."""
    save_personal_info(user_id=user.id, **SCREEN_ONE)

    with pytest.raises(ValidationError) as caught:
        submit_for_review(user_id=user.id)

    assert set(caught.value.details["fields"]) == {
        "city", "address", "employment_status", "income_source",
    }
    assert KYCSubmission.objects.get(user_id=user.id).status == KYCStatus.PENDING


def test_a_complete_record_submits(user: User) -> None:
    save_personal_info(user_id=user.id, **SCREEN_ONE)
    save_personal_info(user_id=user.id, **SCREEN_TWO)

    submission = submit_for_review(user_id=user.id)

    assert submission.status == KYCStatus.MANUAL_REVIEW
    assert submission.submitted_at is not None
