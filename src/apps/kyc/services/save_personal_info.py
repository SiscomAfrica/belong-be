from __future__ import annotations

from datetime import date
from uuid import UUID

from apps.kyc.exceptions import KYCInvalidStateError, KYCNotFoundError
from apps.kyc.models import KYCStatus, KYCSubmission


def save_personal_info(
    *,
    user_id: UUID,
    first_name: str = "",
    last_name: str = "",
    date_of_birth: date | None = None,
    nationality: str = "",
    id_number: str = "",
    kra_pin: str = "",
    city: str = "",
    address: str = "",
    employment_status: str = "",
    income_source: str = "",
    kin_name: str = "",
    kin_phone: str = "",
    kin_email: str = "",
) -> KYCSubmission:
    try:
        submission = KYCSubmission.objects.get(user_id=user_id)
    except KYCSubmission.DoesNotExist:
        raise KYCNotFoundError()

    if submission.status not in (KYCStatus.PENDING, KYCStatus.NOT_STARTED):
        raise KYCInvalidStateError("Cannot update personal info after submission.")

    submission.first_name = first_name
    submission.last_name = last_name
    submission.date_of_birth = date_of_birth
    submission.nationality = nationality
    submission.id_number = id_number
    submission.kra_pin = kra_pin
    submission.city = city
    submission.address = address
    submission.employment_status = employment_status
    submission.income_source = income_source
    submission.kin_name = kin_name
    submission.kin_phone = kin_phone
    submission.kin_email = kin_email
    submission.save()
    return KYCSubmission.objects.prefetch_related("documents").get(pk=submission.pk)
