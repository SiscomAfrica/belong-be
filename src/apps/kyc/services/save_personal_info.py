from __future__ import annotations

from datetime import date
from uuid import UUID

from apps.kyc.exceptions import KYCInvalidStateError
from apps.kyc.models import DocumentType, KYCStatus, KYCSubmission
from apps.kyc.services.personal_info_checks import FIELDS
from apps.kyc.services.validate_personal_info import validate_personal_info


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

    # The ID number is collected on step 1, but the document it came from is
    # not chosen until step 2 — so document_type is still "" when the number
    # first arrives, and validate_document_number has no rule to check it
    # against ("Unknown document type ''").
    #
    # Assume the national ID, which is what the app itself defaults to and
    # what nearly every Kenyan user will pick. start_kyc overwrites this the
    # moment they choose, and submit_for_review re-checks the stored number
    # against whatever they settled on — so guessing here can delay a
    # mismatch, never hide one.
    provisional_document_type = not submission.document_type
    if provisional_document_type:
        submission.document_type = DocumentType.NATIONAL_ID

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

    # document_type is set above rather than validated into `cleaned`, so it
    # belongs in update_fields but never in the loop.
    changed = [*written, "status", "updated_at"]
    if provisional_document_type:
        changed.append("document_type")

    # Narrowed to what was written, so a concurrent save of another screen
    # cannot be undone by this one rewriting its columns from a stale read.
    submission.save(update_fields=changed)
    return KYCSubmission.objects.prefetch_related("documents").get(pk=submission.pk)
