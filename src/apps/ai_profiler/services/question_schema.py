from __future__ import annotations

from apps.ai_profiler.rubric import BEHAVIOUR_KEYS

MIN_OPTIONS = 3
MAX_OPTIONS = 4
MAX_LABEL = 60
MAX_SUBLABEL = 90

# Anchors are carried as {behaviour, value} pairs rather than a keyed object so
# the schema stays strict-mode friendly: strict JSON schema requires every
# declared property to be required, which an optional-keys object cannot honour.

_ANCHOR = {
    "type": "object",
    "properties": {
        "behaviour": {"type": "string", "enum": list(BEHAVIOUR_KEYS)},
        "value": {
            "type": "string",
            "description": "Anchor level as a digit for ordinal behaviours, "
                           "or the category key for categorical ones.",
        },
    },
    "required": ["behaviour", "value"],
    "additionalProperties": False,
}

_OPTION = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "maxLength": MAX_LABEL},
        "sublabel": {"type": "string", "maxLength": MAX_SUBLABEL},
        "anchors": {
            "type": "array",
            "items": _ANCHOR,
            "minItems": 1,
        },
    },
    "required": ["label", "sublabel", "anchors"],
    "additionalProperties": False,
}


def question_schema(*, behaviour: str) -> dict:
    """JSON schema for one generated question targeting `behaviour`."""
    return {
        "type": "object",
        "properties": {
            "primary_behaviour": {"type": "string", "enum": [behaviour]},
            "secondary_behaviours": {
                "type": "array",
                "items": {"type": "string", "enum": list(BEHAVIOUR_KEYS)},
            },
            "question": {"type": "string", "maxLength": 120},
            "subtitle": {"type": "string", "maxLength": 160},
            "options": {
                "type": "array",
                "items": _OPTION,
                "minItems": MIN_OPTIONS,
                "maxItems": MAX_OPTIONS,
            },
        },
        "required": [
            "primary_behaviour",
            "secondary_behaviours",
            "question",
            "subtitle",
            "options",
        ],
        "additionalProperties": False,
    }
