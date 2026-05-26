from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class InvestmentLimitOut(Schema):
    kyc_tier: str
    max_per_transaction: Decimal
    max_per_month: Decimal


class ConsentVersionOut(Schema):
    id: UUID
    document_type: str
    version: str
    effective_date: date
    content_url: str


class ConsentStatusOut(Schema):
    terms_current: bool
    privacy_current: bool


class UserConsentOut(Schema):
    id: UUID
    consent_version: ConsentVersionOut
    accepted_at: datetime
