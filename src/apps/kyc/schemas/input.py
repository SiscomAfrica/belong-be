from __future__ import annotations

from datetime import date

from ninja import Schema
from pydantic import Field


class KYCStartIn(Schema):
    document_type: str = Field(default="NATIONAL_ID", pattern="^(NATIONAL_ID|PASSPORT|DRIVING_LICENSE)$", description="ID document type to verify")


class KYCDocumentUploadIn(Schema):
    side: str = Field(pattern="^(FRONT|BACK)$", description="Document side: FRONT or BACK")
    file_key: str = Field(min_length=1, max_length=500, description="S3 file key of the uploaded document image")


class KYCPersonalInfoIn(Schema):
    first_name: str = Field(default="", max_length=100)
    last_name: str = Field(default="", max_length=100)
    date_of_birth: date | None = Field(default=None)
    nationality: str = Field(default="", max_length=50)
    id_number: str = Field(default="", max_length=50)
    kra_pin: str = Field(default="", max_length=20)
    city: str = Field(default="", max_length=100)
    address: str = Field(default="", max_length=255)
    employment_status: str = Field(default="", max_length=30)
    income_source: str = Field(default="", max_length=30)
    kin_name: str = Field(default="", max_length=100)
    kin_phone: str = Field(default="", max_length=20)
    kin_email: str = Field(default="", max_length=254)


# class KYCSelfieUploadIn(Schema):
#     file_key: str = Field(
#         min_length=1, max_length=500,
#         description="S3 file key of the selfie image",
#     )
