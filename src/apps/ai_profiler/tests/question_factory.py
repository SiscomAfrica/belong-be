from __future__ import annotations

# Builders for generated-question fixtures. Shared by the validation tests so
# each file states only what it is actually asserting.


def anchor(behaviour: str, value: str) -> dict:
    return {"behaviour": behaviour, "value": value}


def option(label: str, *anchors: dict) -> dict:
    return {"label": label, "sublabel": "context", "anchors": list(anchors)}


def risk_levels(*values: str) -> list[dict]:
    """One option per risk anchor, labelled only enough to tell them apart."""
    return [option(f"opt{value}", anchor("risk", value)) for value in values]


def question(**overrides) -> dict:
    """A valid risk question. Override any field to make it invalid."""
    base = {
        "primary_behaviour": "risk",
        "secondary_behaviours": [],
        "question": "How would a sharp drop in your holdings sit with you?",
        "subtitle": "Your answer shapes how we balance stability and growth.",
        "options": [
            option("I'd pull everything out", anchor("risk", "1")),
            option("I'd worry but hold", anchor("risk", "2")),
            option("I'd leave it alone", anchor("risk", "4")),
            option("I'd put more in", anchor("risk", "5")),
        ],
    }
    return {**base, **overrides}
