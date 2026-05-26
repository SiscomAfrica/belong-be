from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class MarketTicker(BaseModel):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    change_pct = models.DecimalField(max_digits=8, decimal_places=4)
    change_value = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    fetched_at = models.DateTimeField()

    class Meta:
        db_table = "market_data_ticker"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.symbol}: {self.price}"
