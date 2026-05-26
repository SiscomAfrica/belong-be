from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema


class ReferralCodeOut(Schema):
    referral_code: str


class ReferralStatsOut(Schema):
    total_referrals: int
    total_conversions: int
    total_creds: int


class ReferralHistoryItemOut(Schema):
    id: UUID
    referred_phone: str
    status: str
    converted_at: datetime | None = None
    creds_awarded: int
    created_at: datetime

    @staticmethod
    def resolve_referred_phone(obj):
        return obj.referred_user.phone


class ReferralHistoryListOut(Schema):
    items: list[ReferralHistoryItemOut]
    count: int


class CredsBalanceOut(Schema):
    balance: int


class CredsLedgerItemOut(Schema):
    id: UUID
    delta: int
    reason: str
    balance_after: int
    created_at: datetime


class CredsLedgerListOut(Schema):
    items: list[CredsLedgerItemOut]
    count: int
