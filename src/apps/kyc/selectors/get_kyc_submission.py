from __future__ import annotations

from uuid import UUID

from apps.kyc.exceptions import KYCNotFoundError
from apps.kyc.models import KYCSubmission


def get_kyc_submission(*, user_id: UUID) -> KYCSubmission:
    try:
        return KYCSubmission.objects.prefetch_related("documents").get(user_id=user_id)
    except KYCSubmission.DoesNotExist:
        raise KYCNotFoundError()
