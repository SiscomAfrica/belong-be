from __future__ import annotations

from ninja import Router

from apps.referrals.schemas import (
    CredsBalanceOut,
    CredsLedgerListOut,
    ReferralCodeOut,
    ReferralHistoryListOut,
    ReferralStatsOut,
)
from apps.referrals.selectors.get_creds_balance import get_creds_balance
from apps.referrals.selectors.get_referral_stats import get_referral_stats
from apps.referrals.selectors.list_creds_ledger import list_creds_ledger
from apps.referrals.selectors.list_referral_history import list_referral_history

referrals_router = Router(tags=["referrals"])


@referrals_router.get("/my-code", response=ReferralCodeOut)
def get_my_code(request):
    """Return the authenticated user's referral code."""
    return ReferralCodeOut(referral_code=request.auth.referral_code)


@referrals_router.get("/stats", response=ReferralStatsOut)
def get_stats(request):
    """Return referral statistics for the authenticated user."""
    stats = get_referral_stats(user_id=request.auth.id)
    return ReferralStatsOut(**stats)


@referrals_router.get("/history", response=ReferralHistoryListOut)
def get_history(request):
    """List all referral invitations and their conversion status."""
    referrals = list_referral_history(user_id=request.auth.id)
    return ReferralHistoryListOut(items=list(referrals), count=referrals.count())


@referrals_router.get("/creds/balance", response=CredsBalanceOut)
def get_balance(request):
    """Return the user's current referral credits balance."""
    balance = get_creds_balance(user_id=request.auth.id)
    return CredsBalanceOut(balance=balance)


@referrals_router.get("/creds/ledger", response=CredsLedgerListOut)
def get_ledger(request):
    """List all credit ledger entries showing earned and spent credits."""
    entries = list_creds_ledger(user_id=request.auth.id)
    return CredsLedgerListOut(items=list(entries), count=entries.count())
