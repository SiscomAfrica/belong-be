from __future__ import annotations

from datetime import date

import pytest

from apps.investments.models.recurring_plan import PlanFrequency
from apps.investments.services.plan_schedule import next_run_after


@pytest.mark.parametrize(
    ("frequency", "expected"),
    [
        (PlanFrequency.DAILY, date(2026, 1, 16)),
        (PlanFrequency.WEEKLY, date(2026, 1, 22)),
        (PlanFrequency.BIWEEKLY, date(2026, 1, 29)),
        (PlanFrequency.MONTHLY, date(2026, 2, 15)),
        (PlanFrequency.BIMONTHLY, date(2026, 3, 15)),
        (PlanFrequency.QUARTERLY, date(2026, 4, 15)),
        (PlanFrequency.HALF_YEARLY, date(2026, 7, 15)),
        (PlanFrequency.YEARLY, date(2027, 1, 15)),
    ],
)
def test_each_cadence_advances_by_its_own_period(frequency, expected) -> None:
    assert next_run_after(start=date(2026, 1, 15), frequency=frequency) == expected


def test_a_one_off_has_no_next_run() -> None:
    """None is the signal to retire the plan, not to schedule it again."""
    assert next_run_after(start=date(2026, 1, 15), frequency=PlanFrequency.ONE_OFF) is None


def test_month_end_does_not_drift_backwards() -> None:
    """timedelta(days=30) walked the 31st back to the 30th, then the 29th."""
    first = next_run_after(start=date(2026, 1, 31), frequency=PlanFrequency.MONTHLY)
    second = next_run_after(start=first, frequency=PlanFrequency.MONTHLY)
    third = next_run_after(start=second, frequency=PlanFrequency.MONTHLY)

    assert first == date(2026, 2, 28)
    assert second == date(2026, 3, 28)
    assert third == date(2026, 4, 28)


def test_every_cadence_is_expressible_as_a_ratiba_frequency() -> None:
    """A plan Ratiba cannot schedule is a plan whose money cannot be collected."""
    from apps.payments.providers.ratiba_request import FREQUENCY_CODES

    assert set(PlanFrequency.values) == set(FREQUENCY_CODES)


def test_an_unknown_cadence_is_rejected_rather_than_guessed() -> None:
    with pytest.raises(ValueError, match="Unknown plan frequency"):
        next_run_after(start=date(2026, 1, 15), frequency="FORTNIGHTLY")


def test_the_ratiba_codes_match_daraja_s_published_table() -> None:
    """Off-by-one here deducts on the wrong cadence, which is real money.

    Daraja's table: 1 One Off, 2 Daily, 3 Weekly, 4 Bi-weekly, 5 Monthly,
    6 Bi-monthly, 7 Quarterly, 8 Half Yearly, 9 Yearly.
    """
    from apps.payments.providers.ratiba_request import FREQUENCY_CODES

    assert FREQUENCY_CODES == {
        "ONE_OFF": "1",
        "DAILY": "2",
        "WEEKLY": "3",
        "BIWEEKLY": "4",
        "MONTHLY": "5",
        "BIMONTHLY": "6",
        "QUARTERLY": "7",
        "HALF_YEARLY": "8",
        "YEARLY": "9",
    }
