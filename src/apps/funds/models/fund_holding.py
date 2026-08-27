from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel
from apps.common.storage import holding_logo_upload_path
from apps.common.validators import validate_image_max_5mb


class FundHolding(BaseModel):
    fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.CASCADE,
        related_name="fund_holdings",
    )
    name = models.CharField(max_length=100)
    logo_image = models.ImageField(
        upload_to=holding_logo_upload_path,
        blank=True,
        default="",
        validators=[validate_image_max_5mb],
    )
    logo_url = models.URLField(blank=True, default="")
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "funds_fund_holding"
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["fund", "name"],
                name="unique_fund_holding_name",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.fund} — {self.name}"
