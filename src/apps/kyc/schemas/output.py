from __future__ import annotations

from datetime import date, datetime
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
    status: str = Field(description="KYC status")
    document_type: str = Field(description="Document type used for verification")
    submitted_at: datetime | None = Field(default=None)
    documents: list[KYCDocumentOut] = Field(description="Uploaded document records")
    created_at: datetime = Field(description="Submission creation timestamp")
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    date_of_birth: date | None = Field(default=None)
    nationality: str = Field(default="")
    id_number: str = Field(default="")
    kra_pin: str = Field(default="")
    city: str = Field(default="")
    address: str = Field(default="")
    employment_status: str = Field(default="")
    income_source: str = Field(default="")
    kin_name: str = Field(default="")
    kin_phone: str = Field(default="")
    kin_email: str = Field(default="")

    @staticmethod
    def resolve_documents(obj) -> list:  # noqa: ANN001
        if hasattr(obj, "prefetched_documents"):
            return obj.prefetched_documents
        return list(obj.documents.all())


class KYCStatusOut(Schema):
    status: str = Field(description="Current KYC status")
    submission_id: UUID | None = Field(default=None, description="Active submission UUID if any")


class KYCWebhookAckOut(Schema):
    status: str = Field(description="Webhook acknowledgement status")
