from __future__ import annotations

from decimal import Decimal

from django.db import models

from apps.common.models.base import BaseModel


class InvestmentSettings(BaseModel):
    """Platform-wide investing rules, editable in the admin.

    A single row. It lives in the database rather than the environment so the
    figure can be changed without a redeploy, and so the change is visible and
    attributable rather than buried in a container's config.
    """

    min_contribution = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("100.00"),
        help_text=(
            "Smallest amount a recurring contribution may collect, in KES. "
            "Whole shillings only — M-Pesa Ratiba cannot deduct a fraction, so "
            "anything below 1 creates plans Safaricom rounds down to nothing. "
            "Separate from a fund's own minimum investment, which governs a "
            "lump sum bought in one go."
        ),
    )

    class Meta:
        db_table = "investments_settings"
        verbose_name = "Investment settings"
        verbose_name_plural = "Investment settings"

    def __str__(self) -> str:
        return f"Minimum contribution: KES {self.min_contribution}"
