from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema
from pydantic import Field


class InvestmentLimitOut(Schema):
    kyc_tier: str = Field(description="User KYC tier determining limits")
    max_per_transaction: Decimal = Field(description="Maximum single transaction amount in KES")
    max_per_month: Decimal = Field(description="Maximum monthly investment amount in KES")


class ConsentVersionOut(Schema):
    id: UUID = Field(description="Consent version identifier")
    document_type: str = Field(description="Document type: TERMS | PRIVACY")
    version: str = Field(description="Semantic version string (e.g. 1.2.0)")
    effective_date: date = Field(description="Date this version became effective")
    content_url: str = Field(description="URL to the full document content")


class ConsentStatusOut(Schema):
    terms_current: bool = Field(description="Whether user accepted the latest terms")
    privacy_current: bool = Field(description="Whether user accepted the latest privacy policy")


class UserConsentOut(Schema):
    id: UUID = Field(description="Consent record identifier")
    consent_version: ConsentVersionOut = Field(description="Accepted consent version details")
    accepted_at: datetime = Field(description="When consent was given")
