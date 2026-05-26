from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class Pool(BaseModel):
    fund = models.OneToOneField(
        "funds.Fund",
        on_delete=models.CASCADE,
        related_name="pool",
    )
    total_units = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    total_aum = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    nav_per_unit = models.DecimalField(max_digits=18, decimal_places=6, default=1)
    underlying = models.JSONField(default=list)

    class Meta:
        db_table = "pools_pool"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Pool: {self.fund_id}"
