from __future__ import annotations

from decimal import Decimal


FREQUENCY_MAP: dict[str, int] = {
    "MONTHLY": 12,
    "WEEKLY": 52,
}


def calculate_projection(
    *,
    goal: Decimal,
    contribution: Decimal,
    frequency: str,
    years: int,
    annual_return_pct: Decimal,
) -> dict:
    periods_per_year = FREQUENCY_MAP.get(frequency.upper(), 12)
    rate = annual_return_pct / Decimal("100")
    annual_contribution = contribution * periods_per_year

    value = Decimal("0")
    total_contributions = Decimal("0")
    data_points: list[dict] = []

    for year in range(1, years + 1):
        value = value * (1 + rate) + annual_contribution
        total_contributions += annual_contribution
        earnings = value - total_contributions

        data_points.append({
            "year": year,
            "value": round(value, 2),
            "contributions": round(total_contributions, 2),
            "earnings": round(earnings, 2),
        })

    final_value = round(value, 2)
    total_earnings = round(final_value - total_contributions, 2)

    return {
        "data_points": data_points,
        "total_contributions": round(total_contributions, 2),
        "total_earnings": total_earnings,
        "final_value": final_value,
    }
