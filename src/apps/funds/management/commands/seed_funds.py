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


def _opt_decimal(entry: dict, key: str) -> Decimal | None:
    return Decimal(entry[key]) if entry.get(key) else None


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
                slug=entry["slug"], defaults=self._defaults(entry),
            )
            self.stdout.write(f"  {'Created' if created else 'Updated'}: {fund.name}")
            underlying = entry.get("underlying", [])
            Pool.objects.update_or_create(fund=fund, defaults={"underlying": underlying})
            self._seed_nav(fund, underlying)
            self._seed_tickers(underlying, now)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(data)} funds."))

    @staticmethod
    def _defaults(e: dict) -> dict:
        p = Decimal(e["projected_annual_return"])
        return {
            "name": e["name"], "description": e["description"],
            "fund_type": e["fund_type"], "category": e["category"],
            "risk_level": e["risk_level"], "currency": e["currency"],
            "minimum_investment": Decimal(e["minimum_investment"]),
            "projected_annual_return": p, "effective_annual_yield": p,
            "annualized_daily_yield": p / 365,
            "ticker_symbol": e.get("ticker_symbol", ""),
            "expense_ratio": _opt_decimal(e, "expense_ratio"),
            "aum": _opt_decimal(e, "aum"),
            "ytd_return": _opt_decimal(e, "ytd_return"),
            "launched_date": e.get("launched_date"),
            "management_type": e.get("management_type", ""),
            "listed_country": e.get("listed_country", ""),
            "fund_manager": e.get("fund_manager", ""),
            "top_holdings": e.get("top_holdings", []),
            "perfect_for": e.get("perfect_for", ""),
            "chart_url": e.get("chart_url", ""),
            "emoji": e.get("emoji", ""),
            "is_trending": e.get("is_trending", False),
        }

    @staticmethod
    def _seed_nav(fund: Fund, underlying: list[dict]) -> None:
        tw = sum(u.get("weight", 0) for u in underlying)
        nav = Decimal("1") if tw == 0 else sum(
            Decimal(str(u["price"])) * u["weight"] / tw for u in underlying
        )
        FundNAV.objects.update_or_create(
            fund=fund, date=date.today(),
            defaults={"nav_value": round(nav, 2), "daily_change_pct": Decimal("0")},
        )

    @staticmethod
    def _seed_tickers(underlying: list[dict], now) -> None:  # noqa: ANN001
        for a in underlying:
            MarketTicker.objects.update_or_create(
                symbol=a["symbol"],
                defaults={
                    "name": a["name"], "price": Decimal(a["price"]),
                    "change_pct": Decimal(a.get("change_pct", "0")),
                    "change_value": Decimal("0"), "fetched_at": now,
                },
            )
