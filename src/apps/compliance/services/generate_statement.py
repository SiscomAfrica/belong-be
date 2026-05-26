from __future__ import annotations

from uuid import UUID

from django.template.loader import render_to_string
from weasyprint import HTML

from apps.investments.models import Holding, Investment, InvestmentStatus
from apps.payments.models import PaymentTransaction
from apps.users.models import User


def generate_statement(*, user_id: UUID, year: int, month: int) -> bytes:
    user = User.objects.get(pk=user_id)
    investments = Investment.objects.filter(
        user_id=user_id,
        status=InvestmentStatus.CONFIRMED,
        confirmed_at__year=year,
        confirmed_at__month=month,
    ).select_related("fund")

    payments = PaymentTransaction.objects.filter(
        user_id=user_id,
        created_at__year=year,
        created_at__month=month,
    )

    holdings = Holding.objects.filter(user_id=user_id).select_related("fund")

    context = {
        "user": user,
        "year": year,
        "month": month,
        "investments": investments,
        "payments": payments,
        "holdings": holdings,
        "total_invested": sum(i.amount for i in investments),
    }

    html_string = render_to_string("compliance/statement.html", context)
    return HTML(string=html_string).write_pdf()
