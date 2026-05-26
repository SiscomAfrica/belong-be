from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class ExchangeRate(BaseModel):
    base_currency = models.CharField(max_length=3)
    quote_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=6)
    source = models.CharField(max_length=50)
    fetched_at = models.DateTimeField()

    class Meta:
        db_table = "market_data_exchange_rate"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["base_currency", "quote_currency"],
                name="unique_currency_pair",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.base_currency}/{self.quote_currency}: {self.rate}"
