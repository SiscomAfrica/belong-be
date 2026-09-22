from __future__ import annotations

import pytest

from apps.common.exceptions import ValidationError
from apps.common.validation import sanitise_text, validate_person_name

# Each of these has a destination in this system: a structlog line, a Tilil
# SMS body, a WeasyPrint statement, and a reviewer's admin page.
PAYLOADS = [
    pytest.param("Ann\x00e", "null byte", id="nul-truncates-c-parsers"),
    pytest.param("Ann\r\nlevel=critical", "control characters", id="crlf-forges-a-log-line"),
    pytest.param("Ann\tOtieno", "control characters", id="tab"),
    pytest.param("Ann‮gpj.exe", "text-direction", id="bidi-override-spoofs-filename"),
    pytest.param("Ann​Otieno", "invisible characters", id="zero-width-space"),
    pytest.param("Ann﻿Otieno", "invisible characters", id="bom"),
]


@pytest.mark.parametrize(("payload", "expected"), PAYLOADS)
def test_dangerous_characters_are_rejected_not_stripped(
    payload: str, expected: str,
) -> None:
    """Rejected rather than cleaned: a name containing a bidi override is not
    a typo, and quietly removing it hides the attempt from the audit trail.
    """
    with pytest.raises(ValidationError, match=expected):
        sanitise_text(value=payload, field="first_name", max_length=100)


@pytest.mark.parametrize(
    "payload",
    [
        "Robert'); DROP TABLE users;--",
        "<script>alert(1)</script>",
        "{{7*7}}",
        "../../etc/passwd",
        "=cmd|'/c calc'!A0",
    ],
)
def test_a_name_field_only_accepts_name_shaped_input(payload: str) -> None:
    with pytest.raises(ValidationError):
        validate_person_name(value=payload, field="first_name")


@pytest.mark.parametrize(
    "name",
    ["Wanjiku", "N'Dour", "Wanjiku-Otieno", "Mary Jane", "J.P. Otieno", "Zoë", "Müller"],
)
def test_real_names_still_pass(name: str) -> None:
    assert validate_person_name(value=name, field="first_name") == name


def test_whitespace_is_collapsed_quietly() -> None:
    """A double space is an ordinary slip, not an attack — so it is fixed,
    not rejected.
    """
    assert sanitise_text(
        value="  Mary   Jane  ", field="first_name", max_length=100,
    ) == "Mary Jane"
