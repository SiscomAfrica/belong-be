from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.funds.models import Fund, FundNAV
from apps.market_data.models import MarketTicker
from apps.pools.models import Pool

DEFAULT_FILE = Path(__file__).resolve().parent.parent.parent.parent.parent / "fixtures" / "funds.json"


class Command(BaseCommand):
    help = "Seed funds, pools, NAV records, and market tickers from JSON."

    def add_arguments(self, parser) -> None:  # noqa: ANN001
        parser.add_argument("--file", type=str, default=str(DEFAULT_FILE))

    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003
        path = Path(options["file"])
        data = json.loads(path.read_text())
        now = timezone.now()

        for entry in data:
            fund, created = Fund.objects.update_or_create(
                slug=entry["slug"],
                defaults={
                    "name": entry["name"],
                    "description": entry["description"],
                    "fund_type": entry["fund_type"],
                    "category": entry["category"],
                    "risk_level": entry["risk_level"],
                    "currency": entry["currency"],
                    "minimum_investment": Decimal(entry["minimum_investment"]),
                    "projected_annual_return": Decimal(entry["projected_annual_return"]),
                    "effective_annual_yield": Decimal(entry["projected_annual_return"]),
                    "annualized_daily_yield": Decimal(entry["projected_annual_return"]) / 365,
                    "emoji": entry.get("emoji", ""),
                    "is_trending": entry.get("is_trending", False),
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action}: {fund.name}")

            underlying = entry.get("underlying", [])
            Pool.objects.get_or_create(
                fund=fund, defaults={"underlying": underlying}
            )

            nav_value = self._weighted_nav(underlying)
            FundNAV.objects.update_or_create(
                fund=fund,
                date=date.today(),
                defaults={"nav_value": nav_value, "daily_change_pct": Decimal("0")},
            )

            for asset in underlying:
                MarketTicker.objects.update_or_create(
                    symbol=asset["symbol"],
                    defaults={
                        "name": asset["name"],
                        "price": Decimal(asset["price"]),
                        "change_pct": Decimal(asset.get("change_pct", "0")),
                        "change_value": Decimal("0"),
                        "fetched_at": now,
                    },
                )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(data)} funds."))

    @staticmethod
    def _weighted_nav(underlying: list[dict]) -> Decimal:
        total_weight = sum(u.get("weight", 0) for u in underlying)
        if total_weight == 0:
            return Decimal("1")
        nav = sum(
            Decimal(str(u["price"])) * u["weight"] / total_weight
            for u in underlying
        )
        return round(nav, 2)
