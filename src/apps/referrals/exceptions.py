from __future__ import annotations

from apps.common.exceptions import ValidationError


class InvalidReferralCodeError(ValidationError):
    code = "INVALID_REFERRAL_CODE"

    def __init__(self) -> None:
        super().__init__("Invalid or unknown referral code.")


class SelfReferralError(ValidationError):
    code = "SELF_REFERRAL"

    def __init__(self) -> None:
        super().__init__("You cannot refer yourself.")
