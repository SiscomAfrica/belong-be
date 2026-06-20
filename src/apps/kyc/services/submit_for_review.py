from __future__ import annotations

from uuid import UUID

from django.utils import timezone

from apps.kyc.exceptions import KYCInvalidStateError, KYCNotFoundError
from apps.kyc.models import KYCStatus, KYCSubmission


def submit_for_review(*, user_id: UUID) -> KYCSubmission:
    try:
        submission = KYCSubmission.objects.get(user_id=user_id)
    except KYCSubmission.DoesNotExist:
        raise KYCNotFoundError()

    if submission.status != KYCStatus.PENDING:
        raise KYCInvalidStateError("KYC must be in PENDING state to submit for review.")

    submission.status = KYCStatus.MANUAL_REVIEW
    submission.submitted_at = timezone.now()
    submission.save()
    return KYCSubmission.objects.prefetch_related("documents").get(pk=submission.pk)
