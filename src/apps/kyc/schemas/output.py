from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema
from pydantic import Field


class KYCDocumentOut(Schema):
    id: UUID = Field(description="Document record identifier")
    side: str = Field(description="Document side: FRONT | BACK | SELFIE")
    file_key: str = Field(description="S3 file key")
    uploaded_at: datetime = Field(description="Upload timestamp")


class KYCSubmissionOut(Schema):
    id: UUID = Field(description="KYC submission identifier")
    status: str = Field(description="Status: PENDING | SUBMITTED | APPROVED | REJECTED")
    document_type: str = Field(description="Document type used for verification")
    smile_job_id: str = Field(description="Smile Identity external job ID")
    submitted_at: datetime | None = Field(default=None, description="When documents were submitted for review")
    documents: list[KYCDocumentOut] = Field(description="Uploaded document records")
    created_at: datetime = Field(description="Submission creation timestamp")

    @staticmethod
    def resolve_documents(obj) -> list:  # noqa: ANN001
        if hasattr(obj, "prefetched_documents"):
            return obj.prefetched_documents
        return list(obj.documents.all())


class KYCStatusOut(Schema):
    status: str = Field(description="Current KYC status: NONE | PENDING | APPROVED | REJECTED")
    submission_id: UUID | None = Field(default=None, description="Active submission UUID if any")


class KYCWebhookAckOut(Schema):
    status: str = Field(description="Webhook acknowledgement status")
