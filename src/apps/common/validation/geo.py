from __future__ import annotations

import pycountry

from apps.common.exceptions import ValidationError
from apps.common.validation.text import sanitise_identifier


def validate_country_code(*, value: str, field: str = "nationality") -> str:
    """Return an ISO 3166-1 alpha-2 code, or raise.

    Stored as the code rather than a demonym: "Kenyan" has no canonical
    spelling, no ordering and no way to be matched against a passport's
    machine-readable zone, while KE has all three. pycountry is the authority
    so the list cannot drift from ISO as countries change.
    """
    # Sanitised generously, then length-checked as part of the lookup: capping
    # at 3 here reports "must be at most 3 characters" for an input like
    # "Kenyan", which tells the user nothing about what is actually wanted.
    cleaned = sanitise_identifier(value=value, field=field, max_length=64)
    if not cleaned:
        raise ValidationError(f"{field} is required.")
    if len(cleaned) not in (2, 3):
        raise ValidationError(
            f"{field} must be a two-letter country code, e.g. KE for Kenya.",
        )

    country = pycountry.countries.get(alpha_2=cleaned)
    if country is None and len(cleaned) == 3:
        # Accept alpha-3 on the way in and normalise it down, so a client
        # sending KEN is corrected rather than rejected.
        country = pycountry.countries.get(alpha_3=cleaned)

    if country is None:
        raise ValidationError(f"{field} is not a recognised country code.")

    return country.alpha_2
