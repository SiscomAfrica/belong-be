from __future__ import annotations

from decimal import Decimal

from apps.investments.models.investment_settings import InvestmentSettings


def get_min_contribution() -> Decimal:
    """Smallest amount a recurring contribution may collect, in KES.

    Reads the single admin-managed settings row, creating it with the field
    default if it is missing — a fresh database should not make plan creation
    fail, and the row then shows up in the admin ready to edit.
    """
    settings_row = InvestmentSettings.objects.first()
    if settings_row is None:
        settings_row = InvestmentSettings.objects.create()
    return settings_row.min_contribution
