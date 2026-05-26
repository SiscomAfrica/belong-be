from __future__ import annotations

from uuid import UUID

from apps.kyc.exceptions import KYCInvalidStateError, KYCNotFoundError
from apps.kyc.models import KYCDocument, KYCStatus, KYCSubmission


def upload_document(*, user_id: UUID, side: str, file_key: str) -> KYCSubmission:
    try:
        submission = KYCSubmission.objects.get(user_id=user_id)
    except KYCSubmission.DoesNotExist:
        raise KYCNotFoundError()

    if submission.status != KYCStatus.PENDING:
        raise KYCInvalidStateError("KYC must be in PENDING state to upload documents.")

    KYCDocument.objects.update_or_create(
        submission=submission,
        side=side,
        defaults={"file_key": file_key},
    )
    return KYCSubmission.objects.prefetch_related("documents").get(pk=submission.pk)
