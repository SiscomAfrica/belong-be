from __future__ import annotations

from decimal import Decimal

import pytest

from apps.funds.models import Fund
from apps.investments.models import Investment, InvestmentStatus
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.payments.services.credit_wallet import credit_wallet
from apps.users.models import User


@pytest.fixture
def user() -> User:
    return User.objects.create(
        phone="+254700000001", username="payer", referral_code="PAYER001",
    )


@pytest.fixture
def fund() -> Fund:
    return Fund.objects.create(
        name="Stable Gains",
        slug="stable-gains",
        description="Test fund.",
        fund_type="ETF",
        category="DIVIDEND",
        risk_level=2,
        currency="KES",
        minimum_investment=Decimal("100.00"),
        projected_annual_return=Decimal("10.00"),
        effective_annual_yield=Decimal("10.00"),
        annualized_daily_yield=Decimal("0.03"),
    )


@pytest.fixture
def investment(user: User, fund: Fund) -> Investment:
    return Investment.objects.create(
        user=user,
        fund=fund,
        amount=Decimal("1000.00"),
        units=Decimal("10.000000"),
        nav_at_purchase=Decimal("100.00"),
        status=InvestmentStatus.PENDING,
        idempotency_key="inv-key-1",
    )


@pytest.fixture
def make_payment(user: User):
    """A payment sitting in INITIATED, optionally tied to an investment."""
    def _make(*, investment: Investment | None = None, amount: str = "1000.00"):
        return PaymentTransaction.objects.create(
            user=user,
            investment=investment,
            provider="MPESA",
            status=PaymentStatus.INITIATED,
            amount=Decimal(amount),
            phone_number="+254700000001",
            external_ref=f"ref-{investment.id if investment else 'topup'}",
            idempotency_key=f"pay-{investment.id if investment else 'topup'}",
        )

    return _make


@pytest.fixture
def funded_user(user: User) -> User:
    credit_wallet(user_id=user.id, amount=Decimal("1000.00"), currency="KES")
    return user


@pytest.fixture
def admin() -> User:
    return User.objects.create(
        phone="+254700000009", username="admin", referral_code="ADMIN001",
    )
