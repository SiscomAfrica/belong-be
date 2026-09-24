from __future__ import annotations

from decimal import Decimal

import pytest

from apps.funds.models import Fund
from apps.investments.models import Investment, InvestmentStatus
from apps.kyc.models import KYCStatus, KYCSubmission
from apps.kyc.services.apply_kyc_decision import apply_kyc_decision
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return User.objects.create(
        phone="+254726721982", username="mk", referral_code="MANUAL001",
    )


@pytest.fixture
def fund() -> Fund:
    return Fund.objects.create(
        name="All in One Stack", slug="all-in-one", ticker_symbol="AIO",
        fund_type="ETF", category="GENERAL", risk_level=3, currency="USD",
        minimum_investment=Decimal("1.00"),
        projected_annual_return=Decimal("10.00"),
        effective_annual_yield=Decimal("10.00"),
        annualized_daily_yield=Decimal("0.03"),
    )


def pending_kyc_investment(user: User, fund: Fund) -> Investment:
    return Investment.objects.create(
        user=user, fund=fund, amount=Decimal("1.00"), units=Decimal("1.0"),
        nav_at_purchase=Decimal("1.00"), status=InvestmentStatus.PENDING_KYC,
        idempotency_key=f"inv-{user.pk}",
    )


def paid(investment: Investment) -> PaymentTransaction:
    return PaymentTransaction.objects.create(
        user=investment.user, investment=investment, provider="MPESA",
        status=PaymentStatus.SUCCESS, amount=investment.amount,
        phone_number=investment.user.phone, idempotency_key=f"pay-{investment.pk}",
    )


@pytest.fixture
def submission(user: User) -> KYCSubmission:
    return KYCSubmission.objects.create(
        user=user, status=KYCStatus.MANUAL_REVIEW, document_type="NATIONAL_ID",
    )


def test_approving_confirms_an_investment_that_was_already_paid_for(
    user: User, fund: Fund, submission: KYCSubmission,
) -> None:
    """The bug this exists to prevent.

    settle_successful_payment deliberately leaves a PENDING_KYC investment
    alone, for the KYC decision to finish. Approving in the admin used to be a
    queryset update that wrote the status column and nothing else — so nothing
    finished it. The payment had succeeded, the member was verified, and the
    money had bought nothing.
    """
    investment = pending_kyc_investment(user, fund)
    paid(investment)

    apply_kyc_decision(submission=submission, verified=True)

    investment.refresh_from_db()
    assert investment.status == InvestmentStatus.CONFIRMED


def test_approving_releases_an_unpaid_investment_to_pending(
    user: User, fund: Fund, submission: KYCSubmission,
) -> None:
    """Verified but unpaid is not confirmed — it just stops waiting on KYC."""
    investment = pending_kyc_investment(user, fund)

    apply_kyc_decision(submission=submission, verified=True)

    investment.refresh_from_db()
    assert investment.status == InvestmentStatus.PENDING


def test_rejecting_leaves_investments_alone(
    user: User, fund: Fund, submission: KYCSubmission,
) -> None:
    investment = pending_kyc_investment(user, fund)
    paid(investment)

    apply_kyc_decision(submission=submission, verified=False, result_text="Blurry ID")

    investment.refresh_from_db()
    assert investment.status == InvestmentStatus.PENDING_KYC
    submission.refresh_from_db()
    assert submission.status == KYCStatus.REJECTED
