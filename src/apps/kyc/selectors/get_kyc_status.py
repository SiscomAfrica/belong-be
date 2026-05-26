from __future__ import annotations

from uuid import UUID

from apps.kyc.models import KYCStatus, KYCSubmission


def get_kyc_status(*, user_id: UUID) -> dict:
    try:
        submission = KYCSubmission.objects.get(user_id=user_id)
        return {"status": submission.status, "submission_id": submission.id}
    except KYCSubmission.DoesNotExist:
        return {"status": KYCStatus.NOT_STARTED, "submission_id": None}
