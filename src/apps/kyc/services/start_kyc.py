from __future__ import annotations

from uuid import UUID

from apps.audit.models import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.kyc.exceptions import KYCAlreadySubmittedError
from apps.kyc.models import KYCStatus, KYCSubmission


def start_kyc(*, user_id: UUID, document_type: str) -> KYCSubmission:
    submission, created = KYCSubmission.objects.get_or_create(
        user_id=user_id,
        defaults={"document_type": document_type, "status": KYCStatus.PENDING},
    )
    if not created:
        if submission.status in (KYCStatus.VERIFIED, KYCStatus.PROCESSING):
            raise KYCAlreadySubmittedError()
        submission.status = KYCStatus.PENDING
        submission.document_type = document_type
        submission.smile_job_id = ""
        submission.result_text = ""
        submission.submitted_at = None
        submission.save()

    create_audit_log(
        action=AuditAction.KYC_SUBMITTED,
        actor_id=user_id,
        entity_type="KYCSubmission",
        entity_id=submission.id,
        new_values={"document_type": document_type},
    )
    return KYCSubmission.objects.prefetch_related("documents").get(pk=submission.pk)
