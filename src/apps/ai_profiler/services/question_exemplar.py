from __future__ import annotations

from apps.ai_profiler.rubric import BEHAVIOUR_KEYS, ORDINAL_ANCHORS, ORDINAL_KEYS
from apps.ai_profiler.services.fallback_questions import fallback_questions


def style_exemplar(*, behaviour: str) -> str:
    """A banked question, shown for tone only.

    Deliberately a *different* behaviour from the one being written, so the
    model copies the register and not the question. Chosen by position rather
    than at random so the same behaviour always gets the same exemplar, which
    keeps a prompt reproducible when a generation is being debugged.
    """
    banked = [
        question
        for question in fallback_questions()
        if question.get("primary_behaviour") != behaviour
    ]
    if not banked:
        return ""

    keys = list(BEHAVIOUR_KEYS)
    index = keys.index(behaviour) if behaviour in keys else 0
    example = banked[index % len(banked)]

    return "\n".join(
        (
            "This is the register we want. Study the voice, not the subject — "
            "you are writing about something else:",
            f"  Question: {example['question']}",
            f"  Subtitle: {example.get('subtitle', '')}",
            *_exemplar_options(example=example),
        ),
    )


def _exemplar_options(*, example: dict) -> list[str]:
    """Two options, each paired with the clinical anchor it was written from.

    Pairing them is the whole point: it shows the model the distance between
    how we define a level internally and how the option is allowed to sound.
    """
    primary = example.get("primary_behaviour", "")
    anchors = ORDINAL_ANCHORS.get(primary, {}) if primary in ORDINAL_KEYS else {}
    lines = []

    for option in example.get("options", [])[:2]:
        value = next(
            (
                anchor["value"]
                for anchor in option.get("anchors", [])
                if anchor.get("behaviour") == primary
            ),
            None,
        )
        lines.append(f"  Option: {option['label']} — {option.get('sublabel', '')}")
        definition = anchors.get(int(value)) if value and str(value).isdigit() else None
        if definition:
            lines.append(f"    (written from the internal anchor: {definition})")

    return lines
