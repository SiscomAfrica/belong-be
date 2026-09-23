from __future__ import annotations

from datetime import date
from uuid import UUID

from apps.kyc.exceptions import KYCInvalidStateError
from apps.kyc.models import KYCStatus, KYCSubmission
from apps.kyc.services.validate_personal_info import validate_personal_info

# The fields this endpoint owns, in the order a reviewer reads them.
FIELDS = (
    "first_name",
    "last_name",
    "date_of_birth",
    "nationality",
    "id_number",
    "kra_pin",
    "city",
    "address",
    "employment_status",
    "income_source",
    "kin_name",
    "kin_phone",
    "kin_email",
)


def save_personal_info(
    *,
    user_id: UUID,
    partial: bool = True,
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
    submission, _ = KYCSubmission.objects.get_or_create(
        user_id=user_id,
        defaults={"status": KYCStatus.PENDING},
    )

    allowed = (KYCStatus.PENDING, KYCStatus.NOT_STARTED, KYCStatus.REJECTED)
    if submission.status not in allowed:
        raise KYCInvalidStateError("Cannot update personal info after submission.")

    if submission.status == KYCStatus.REJECTED:
        submission.status = KYCStatus.PENDING

    # Validated here rather than in the schema because the ID number's format
    # depends on `document_type`, which lives on the submission — the payload
    # never carries it. Raises with every field problem at once.
    #
    # Partial by default: the form spans three screens and each saves only what
    # it collected. A screen that does not hold a field sends nothing for it
    # and nothing is written, instead of the blank it would otherwise overwrite
    # the stored answer with. Completeness is checked once, at submit_for_review.
    cleaned = validate_personal_info(
        data={
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "nationality": nationality,
            "id_number": id_number,
            "kra_pin": kra_pin,
            "city": city,
            "address": address,
            "employment_status": employment_status,
            "income_source": income_source,
            "kin_name": kin_name,
            "kin_phone": kin_phone,
            "kin_email": kin_email,
        },
        document_type=submission.document_type,
        partial=partial,
    )

    # Only what came back cleaned: in partial mode the unsupplied fields are
    # absent from the dict entirely, which is what keeps them untouched.
    written = [field for field in FIELDS if field in cleaned]
    for field in written:
        setattr(submission, field, cleaned[field])

    # Narrowed to what was written, so a concurrent save of another screen
    # cannot be undone by this one rewriting its columns from a stale read.
    submission.save(update_fields=[*written, "status", "updated_at"])
    return KYCSubmission.objects.prefetch_related("documents").get(pk=submission.pk)
