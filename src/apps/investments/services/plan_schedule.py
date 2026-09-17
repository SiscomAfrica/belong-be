from __future__ import annotations

from datetime import date

from dateutil.relativedelta import relativedelta

from apps.investments.models.recurring_plan import PlanFrequency

# Calendar deltas, not fixed day counts. MONTHLY used to be timedelta(days=30),
# which walks backwards through the month — a plan starting on the 31st drifts
# to the 30th, then the 29th. relativedelta keeps the day-of-month stable and
# clamps February correctly.
_OFFSETS = {
    PlanFrequency.DAILY: relativedelta(days=1),
    PlanFrequency.WEEKLY: relativedelta(weeks=1),
    PlanFrequency.BIWEEKLY: relativedelta(weeks=2),
    PlanFrequency.MONTHLY: relativedelta(months=1),
    PlanFrequency.BIMONTHLY: relativedelta(months=2),
    PlanFrequency.QUARTERLY: relativedelta(months=3),
    PlanFrequency.HALF_YEARLY: relativedelta(months=6),
    PlanFrequency.YEARLY: relativedelta(years=1),
}


def next_run_after(*, start: date, frequency: str) -> date | None:
    """Date of the contribution following `start`.

    Returns None for ONE_OFF, which has no next run — the caller deactivates
    the plan instead of scheduling another sweep.
    """
    if frequency == PlanFrequency.ONE_OFF:
        return None

    try:
        return start + _OFFSETS[frequency]
    except KeyError:
        msg = f"Unknown plan frequency: {frequency}"
        raise ValueError(msg) from None
