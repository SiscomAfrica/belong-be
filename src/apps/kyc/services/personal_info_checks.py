from __future__ import annotations

from typing import Any

from apps.common.exceptions import ValidationError
from apps.common.validation import (
    sanitise_text,
    validate_choice,
    validate_country_code,
    validate_date_of_birth,
    validate_document_number,
    validate_kra_pin,
    validate_mobile_e164,
    validate_person_name,
)
from apps.kyc.models import EmploymentStatus, IncomeSource
from apps.kyc.services.validate_contact import validate_email

# Builds already shipped offer only four nationalities, the last of which is
# "other". That is not a country code, so it cannot be stored as one — a
# reviewer reads nationality off the document anyway. Mapped to empty rather
# than rejected, or every one of those users is blocked mid-KYC by an app
# update they cannot install.
_LEGACY_UNKNOWN_NATIONALITY = "OTHER"

# The fields this endpoint owns, in the order a reviewer reads them. Kept
# beside the checks so a field cannot be added to one and forgotten in the
# other.
FIELDS = (
    "first_name",
    "last_name",
    "date_of_birth",
    "nationality",
    "id_number",
    "kra_pin",
    "city",
    "address",
    "employment_status",
    "income_source",
    "kin_name",
    "kin_phone",
    "kin_email",
)


def checks(*, document_type: str) -> dict[str, Any]:
    """One callable per field. `document_type` is closed over because the ID
    number's format depends on which document it came from.
    """
    return {
        "first_name": lambda v: validate_person_name(value=v or "", field="first_name"),
        "last_name": lambda v: validate_person_name(value=v or "", field="last_name"),
        "date_of_birth": _date_of_birth,
        "nationality": _nationality,
        "id_number": lambda v: validate_document_number(
            value=v or "", document_type=document_type,
        ),
        "kra_pin": lambda v: validate_kra_pin(value=v or ""),
        "city": lambda v: _required_text(v, field="city", max_length=100),
        "address": lambda v: _required_text(v, field="address", max_length=255),
        "employment_status": lambda v: validate_choice(
            value=v or "", allowed=EmploymentStatus, field="employment_status",
        ),
        "income_source": lambda v: validate_choice(
            value=v or "", allowed=IncomeSource, field="income_source",
        ),
        "kin_name": lambda v: _optional_name(v, field="kin_name"),
        "kin_phone": lambda v: validate_mobile_e164(value=v, field="kin_phone") if v else "",
        "kin_email": lambda v: validate_email(value=v, field="kin_email") if v else "",
    }


def _date_of_birth(value: Any) -> Any:
    if value is None:
        raise ValidationError("date_of_birth is required.")
    return validate_date_of_birth(value=value)


def _nationality(value: Any) -> str:
    raw = (value or "").strip()
    if raw.upper() == _LEGACY_UNKNOWN_NATIONALITY:
        return ""
    return validate_country_code(value=raw)


def _required_text(value: Any, *, field: str, max_length: int) -> str:
    cleaned = sanitise_text(value=value or "", field=field, max_length=max_length)
    if not cleaned:
        raise ValidationError(f"{field} is required.")
    return cleaned


def _optional_name(value: Any, *, field: str) -> str:
    return validate_person_name(value=value, field=field) if value else ""
