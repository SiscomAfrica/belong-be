from __future__ import annotations

from uuid import UUID

from django.utils import timezone

from apps.kyc.exceptions import KYCInvalidStateError, KYCNotFoundError
from apps.kyc.models import KYCStatus, KYCSubmission
from apps.kyc.services.personal_info_checks import FIELDS
from apps.kyc.services.validate_personal_info import validate_personal_info


def submit_for_review(*, user_id: UUID) -> KYCSubmission:
    """Hand a completed submission to a reviewer.

    This is the only place completeness is required. Saving is partial by
    design — the form spans three screens, and each stores what it collected
    without being able to answer for the others — so a half-filled record is
    an ordinary intermediate state, not an error. It stops being acceptable
    here, where a reviewer is about to be asked to act on it.
    """
    try:
        submission = KYCSubmission.objects.get(user_id=user_id)
    except KYCSubmission.DoesNotExist:
        raise KYCNotFoundError() from None

    if submission.status != KYCStatus.PENDING:
        raise KYCInvalidStateError("KYC must be in PENDING state to submit for review.")

    # Re-validated in full, against what was stored rather than what was sent:
    # the gaps left by partial saves surface here, keyed by field, so the app
    # can say which screen still needs answering.
    validate_personal_info(
        data={field: getattr(submission, field) for field in FIELDS},
        document_type=submission.document_type,
        partial=False,
    )

    submission.status = KYCStatus.MANUAL_REVIEW
    submission.submitted_at = timezone.now()
    submission.save()
    return KYCSubmission.objects.prefetch_related("documents").get(pk=submission.pk)
