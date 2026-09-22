from __future__ import annotations

from apps.common.exceptions import ValidationError
from apps.common.validation.text import sanitise_identifier


def validate_choice(
    *, value: str, allowed: type, field: str, required: bool = True,
) -> str:
    """Normalise a client-supplied value onto a TextChoices member.

    Upper-cased before matching, because builds already in users' hands send
    these fields lower-cased ("employed", "salary") from hardcoded picker
    lists. Rejecting those would break KYC for every installed app until
    everyone updated — and an app release cannot be forced. The stored value
    is always the canonical upper-case member.
    """
    cleaned = sanitise_identifier(value=value, field=field, max_length=32)
    if not cleaned:
        if required:
            raise ValidationError(f"{field} is required.")
        return ""

    if cleaned in allowed.values:
        return cleaned

    options = ", ".join(sorted(allowed.values))
    raise ValidationError(f"{field} must be one of: {options}.")
