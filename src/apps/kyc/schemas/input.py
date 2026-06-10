from __future__ import annotations

from ninja import Schema
from pydantic import Field


class KYCStartIn(Schema):
    document_type: str = Field(pattern="^(NATIONAL_ID|PASSPORT|DRIVING_LICENSE)$", description="ID document type to verify")


class KYCDocumentUploadIn(Schema):
    side: str = Field(pattern="^(FRONT|BACK)$", description="Document side: FRONT or BACK")
    file_key: str = Field(min_length=1, max_length=500, description="S3 file key of the uploaded document image")


class KYCSelfieUploadIn(Schema):
    file_key: str = Field(min_length=1, max_length=500, description="S3 file key of the selfie image")
