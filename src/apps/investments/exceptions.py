from __future__ import annotations

from apps.common.exceptions import ConflictError, NotFoundError, ValidationError


class FundNotActiveError(ValidationError):
    code = "FUND_NOT_ACTIVE"

    def __init__(self) -> None:
        super().__init__("Fund is not active for investments.")


class BelowMinimumInvestmentError(ValidationError):
    code = "BELOW_MINIMUM_INVESTMENT"

    def __init__(self, minimum: str) -> None:
        super().__init__(f"Amount is below minimum investment of {minimum}.")


class NoNAVDataError(ValidationError):
    code = "NO_NAV_DATA"

    def __init__(self) -> None:
        super().__init__("No NAV data available for this fund.")


class PlanNotFoundError(NotFoundError):
    code = "PLAN_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Recurring plan not found.")


class PlanNotActiveError(ValidationError):
    code = "PLAN_NOT_ACTIVE"

    def __init__(self) -> None:
        super().__init__("Recurring plan is not active.")


class GoalNotFoundError(NotFoundError):
    code = "GOAL_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Investment goal not found.")


class DuplicateActivePlanError(ConflictError):
    code = "DUPLICATE_ACTIVE_PLAN"

    def __init__(self) -> None:
        super().__init__("An active plan already exists for this fund.")


class StandingOrderLockedError(ConflictError):
    code = "STANDING_ORDER_LOCKED"

    def __init__(self) -> None:
        super().__init__(
            "This plan is funded by an M-PESA standing order, which cannot be "
            "amended. Cancel it in the M-PESA menu, then create a new plan."
        )


class BelowMinimumContributionError(ValidationError):
    code = "BELOW_MINIMUM_CONTRIBUTION"

    def __init__(self, minimum: str) -> None:
        super().__init__(f"Contribution must be at least KES {minimum}.")
