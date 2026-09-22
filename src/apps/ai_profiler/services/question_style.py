from __future__ import annotations

from apps.ai_profiler.rubric import ORDINAL_KEYS

# How a question should sound. Kept apart from the per-question instruction
# because it is the same every time, and because it is the part worth editing
# when the questions start reading like a form.

VOICE_RULES = """How to write it:
- Speak to one person, as "you". Contractions are good.
- Put them in a concrete moment, not an abstract self-rating. "Your balance
  drops sharply over a bad month" beats "How do you feel about risk?".
- Write every option as something the person would actually say out loud,
  in their own voice, starting with "I" where it fits.
- One idea per option. Never bundle two reactions into the same choice.
- Kenyan life is welcome when it fits naturally — rent, school fees, a side
  business, sending money home. Never assume income, employment or family.
- Never write "Which of the following best describes", "On a scale of",
  "Select the option that", or "Rate your". If it could appear on a form,
  rewrite it."""

SUBTITLE_RULES = """The subtitle is one short line under the question. Use it to take
the pressure off ("There's no wrong answer") or to say plainly why you are asking.
Never restate the question, and never instruct ("Select one")."""


def anchor_guidance(*, behaviour: str, lines: str) -> str:
    """Frame the anchors as a private scale, not as copy to reuse.

    The anchor text is written for us, in clinical language, and handing it to
    a generator without saying so is what produced options like "Cannot
    tolerate loss of capital". It is a definition to classify against — the
    option's wording has to be invented fresh.

    Ordinal and categorical behaviours are tagged differently (a level number
    versus a category key), so the instruction has to name the right one:
    telling the model to "tag it with the number" for `market` invites values
    that check_anchors then rejects.
    """
    if behaviour in ORDINAL_KEYS:
        opening = f"This is our private scale for {behaviour}."
        tag = "the number whose definition it matches"
    else:
        opening = f"These are the categories we sort {behaviour} into."
        tag = "the KEY in capitals whose definition it matches"

    return (
        f"{opening} The wording is internal and must never reach the user — "
        "do not paraphrase it, quote it, or let it set your register. Write "
        "each option in ordinary speech, then tag it with "
        f"{tag}:\n"
        f"{lines}"
    )
