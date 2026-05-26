from __future__ import annotations

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

FREQUENCY_PERIODS: dict[str, int] = {
    "DAILY": 365,
    "WEEKLY": 52,
    "BIWEEKLY": 26,
    "MONTHLY": 12,
}

TWO_PLACES = Decimal("0.01")


def _round(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def calculate_simulation(
    *,
    goal: Decimal,
    contribution: Decimal,
    frequency: str,
    years: int,
    avg_return: Decimal,
) -> dict:
    periods_per_year = FREQUENCY_PERIODS[frequency]
    rate_per_period = avg_return / Decimal(100) / Decimal(periods_per_year)
    total_periods = periods_per_year * years

    # How many contribution periods equal one month
    periods_per_month = max(periods_per_year // 12, 1)

    value = Decimal(0)
    total_contributions = Decimal(0)
    months_to_goal: int | None = None
    chart_data_points: list[dict] = []
    today = date.today()
    month_counter = 0

    for period in range(1, total_periods + 1):
        value = value * (1 + rate_per_period) + contribution
        total_contributions += contribution

        # Sample a chart point every month
        if period % periods_per_month == 0:
            month_counter += 1
            point_date = today + timedelta(days=month_counter * 30)
            chart_data_points.append(
                {"date": point_date, "value": _round(value)},
            )

        # Track first time value exceeds goal
        if months_to_goal is None and value >= goal:
            elapsed_months = period // periods_per_month
            months_to_goal = max(elapsed_months, 1)

    total_earnings = value - total_contributions

    return {
        "projected_final_value": _round(value),
        "months_to_goal": months_to_goal,
        "total_contributions": _round(total_contributions),
        "total_earnings": _round(total_earnings),
        "chart_data_points": chart_data_points,
    }
