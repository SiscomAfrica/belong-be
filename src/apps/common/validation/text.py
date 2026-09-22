from __future__ import annotations

import re
import unicodedata

from apps.common.exceptions import ValidationError

# Every string below reaches a log line, an SMS payload, a PDF statement and a
# reviewer's screen. None of those need a control character, and each of them
# can be damaged by one: a CR or LF forges a log entry or splits an SMS body,
# a NUL truncates a C-string parser, and a bidi override makes text render in
# an order that does not match the bytes stored.

_NUL = "\x00"

# C0 and C1 controls, minus nothing — no field here has a legitimate use for
# tab, carriage return or newline.
_CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f]")

# Bidi overrides and isolates. "‮" can display 'gpj.exe' as 'exe.jpg'.
_BIDI = re.compile(r"[‪-‮⁦-⁩‎‏]")

# Invisible characters: zero-width space/joiners, BOM, word joiner. Used to
# slip past exact-match checks and to make two distinct values look identical.
_INVISIBLE = re.compile(r"[​-‍⁠﻿­]")

_WHITESPACE_RUN = re.compile(r"\s+")


def sanitise_text(*, value: str, field: str, max_length: int) -> str:
    """Normalise a human-entered string, or reject it outright.

    Rejects rather than strips anything that suggests tampering — a name with
    a bidi override in it is not a typo, and silently cleaning it would hide
    the attempt from the audit log. Whitespace is the one thing collapsed
    quietly, because a double space is an ordinary slip.

    Uses NFC, not NFKC: canonical composition without compatibility folding.
    NFKC would rewrite legitimate text — the fi-ligature becomes two letters,
    a vulgar-fraction one-half becomes three characters — which is wrong for a
    legal name that has to match a document exactly.
    """
    if _NUL in value:
        raise ValidationError(f"{field} contains a null byte.")
    if _CONTROL.search(value):
        raise ValidationError(f"{field} contains control characters.")
    if _BIDI.search(value):
        raise ValidationError(f"{field} contains text-direction overrides.")
    if _INVISIBLE.search(value):
        raise ValidationError(f"{field} contains invisible characters.")

    cleaned = _WHITESPACE_RUN.sub(" ", unicodedata.normalize("NFC", value)).strip()

    if len(cleaned) > max_length:
        raise ValidationError(f"{field} must be at most {max_length} characters.")

    return cleaned


def sanitise_identifier(*, value: str, field: str, max_length: int) -> str:
    """As `sanitise_text`, for machine-readable identifiers.

    Folds to NFKC and upper-cases, because an identifier is compared exactly:
    a fullwidth capital A and an ASCII 'A' are the same ID number to a human
    reading the document, and two different rows to the database.
    """
    cleaned = sanitise_text(value=value, field=field, max_length=max_length)
    return unicodedata.normalize("NFKC", cleaned).replace(" ", "").upper()
