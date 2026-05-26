from __future__ import annotations

from ninja import Schema
from pydantic import Field


class KYCStartIn(Schema):
    document_type: str = Field(pattern="^(NATIONAL_ID|PASSPORT|DRIVING_LICENSE)$")


class KYCDocumentUploadIn(Schema):
    side: str = Field(pattern="^(FRONT|BACK)$")
    file_key: str = Field(min_length=1, max_length=500)


class KYCSelfieUploadIn(Schema):
    file_key: str = Field(min_length=1, max_length=500)
