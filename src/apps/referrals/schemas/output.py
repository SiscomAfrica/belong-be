from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ninja import Schema
from pydantic import Field


class ReferralCodeOut(Schema):
    referral_code: str = Field(description="User's shareable referral code")


class ReferralStatsOut(Schema):
    total_referrals: int = Field(description="Total number of referral invites sent")
    total_conversions: int = Field(description="Number of referred users who registered")
    total_creds: int = Field(description="Total credits earned from referrals")


class ReferralHistoryItemOut(Schema):
    id: UUID = Field(description="Referral record identifier")
    referred_phone: str = Field(description="Masked phone of the referred user")
    status: str = Field(description="Status: PENDING | CONVERTED")
    converted_at: datetime | None = Field(default=None, description="When the referred user completed registration")
    creds_awarded: int = Field(description="Credits awarded for this referral")
    created_at: datetime = Field(description="Referral creation timestamp")

    @staticmethod
    def resolve_referred_phone(obj):
        return obj.referred_user.phone


class ReferralHistoryListOut(Schema):
    items: list[ReferralHistoryItemOut] = Field(description="List of referral records")
    count: int = Field(description="Total number of referrals")


class CredsBalanceOut(Schema):
    balance: int = Field(description="Current referral credits balance")


class CredsLedgerItemOut(Schema):
    id: UUID = Field(description="Ledger entry identifier")
    delta: int = Field(description="Credits change (+earned or -spent)")
    reason: str = Field(description="Reason for the credit change")
    balance_after: int = Field(description="Balance after this transaction")
    created_at: datetime = Field(description="Ledger entry timestamp")


class CredsLedgerListOut(Schema):
    items: list[CredsLedgerItemOut] = Field(description="List of credit ledger entries")
    count: int = Field(description="Total number of ledger entries")
