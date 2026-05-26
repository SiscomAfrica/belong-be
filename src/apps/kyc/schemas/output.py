from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema


class KYCDocumentOut(Schema):
    id: UUID
    side: str
    file_key: str
    uploaded_at: datetime


class KYCSubmissionOut(Schema):
    id: UUID
    status: str
    document_type: str
    smile_job_id: str
    submitted_at: datetime | None
    documents: list[KYCDocumentOut]
    created_at: datetime

    @staticmethod
    def resolve_documents(obj) -> list:  # noqa: ANN001
        if hasattr(obj, "prefetched_documents"):
            return obj.prefetched_documents
        return list(obj.documents.all())


class KYCStatusOut(Schema):
    status: str
    submission_id: UUID | None


class KYCWebhookAckOut(Schema):
    status: str
