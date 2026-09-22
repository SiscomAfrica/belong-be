from __future__ import annotations

import re
from datetime import date

from django.utils import timezone

from apps.common.exceptions import ValidationError
from apps.common.validation.text import sanitise_text

# A legal name has to match a government document, so the allowed set is wide
# enough for real Kenyan and international names — letters in any script,
# spaces, hyphens (Wanjiku-Otieno), apostrophes (N'Dour) and full stops
# (initials) — and nothing else. Digits and punctuation are what a payload
# looks like, not what a name looks like.
_NAME = re.compile(r"^[^\W\d_](?:[^\W\d_]|[ \-'.])*$", re.UNICODE)

# CMA/DDPC: a client has to have legal capacity to contract.
MIN_AGE_YEARS = 18
# Older than any living person; a date beyond this is a typo or a probe.
MAX_AGE_YEARS = 120


def validate_person_name(*, value: str, field: str) -> str:
    cleaned = sanitise_text(value=value, field=field, max_length=100)
    if not cleaned:
        raise ValidationError(f"{field} is required.")
    # One character is enough: a single-character given name is ordinary in
    # Chinese and Korean, and nationality is no longer restricted to four
    # countries. A one-letter typo getting through costs a reviewer a glance;
    # a rejected legal name costs the customer the account.
    if not _NAME.match(cleaned):
        raise ValidationError(
            f"{field} may only contain letters, spaces, hyphens and apostrophes.",
        )
    return cleaned


def validate_date_of_birth(*, value: date, field: str = "date_of_birth") -> date:
    """Reject a date that cannot belong to an eligible client.

    Checked here rather than left to a reviewer because age is the one KYC
    field with a hard regulatory answer: under 18 cannot hold the account at
    all, so there is nothing for a human to weigh up.
    """
    today = timezone.localdate()

    if value > today:
        raise ValidationError(f"{field} cannot be in the future.")

    age = _years_between(born=value, today=today)

    if age < MIN_AGE_YEARS:
        raise ValidationError(
            f"You must be at least {MIN_AGE_YEARS} to open an account.",
        )
    if age > MAX_AGE_YEARS:
        raise ValidationError(f"{field} does not look right — please check it.")

    return value


def _years_between(*, born: date, today: date) -> int:
    """Whole years, counting a birthday that has not arrived yet as not had.

    `(today - born).days // 365` drifts by a day per leap year and would let
    someone through the day before their eighteenth birthday.
    """
    had_birthday = (today.month, today.day) >= (born.month, born.day)
    return today.year - born.year - (0 if had_birthday else 1)
