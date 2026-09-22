from __future__ import annotations

import logging

from django.conf import settings

from apps.ai_profiler.providers import get_llm_provider
from apps.ai_profiler.services.fallback_questions import fallback_for
from apps.ai_profiler.services.question_prompt import build_generation_prompt
from apps.ai_profiler.services.question_schema import question_schema
from apps.ai_profiler.services.validate_question import validate_question

logger = logging.getLogger(__name__)


def generate_question(*, behaviour: str, asked: list[dict] | None = None) -> dict:
    """Produce one validated question targeting `behaviour`.

    Retries on invalid output, then falls back to the banked question. The
    caller always receives something usable — onboarding never stalls on a
    generation failure, and a fallback grades identically to a generated one.
    """
    try:
        provider = get_llm_provider()
    except Exception:
        # get_llm_provider raises on an unrecognised LLM_PROVIDER value, which
        # would otherwise 500 the endpoint over a typo in an env var. The
        # questionnaire can run perfectly well without a model.
        logger.exception("Could not build an LLM provider; serving banked questions")
        return _fallback(behaviour=behaviour)

    if not provider.is_configured():
        # No credential, so every attempt can only 401. Skipping straight to
        # the bank saves three doomed round-trips — about 1.5s the user was
        # paying per question for a call that never had a chance.
        logger.warning(
            "LLM provider %s has no API key; serving banked questions. "
            "Run `manage.py check_llm` to confirm.",
            type(provider).__name__,
        )
        return _fallback(behaviour=behaviour)

    schema = question_schema(behaviour=behaviour)
    prompt = build_generation_prompt(behaviour=behaviour, asked=asked or [])
    retries = getattr(settings, "LLM_GENERATION_RETRIES", 2)
    timeout = getattr(settings, "LLM_GENERATION_TIMEOUT", 20)

    for attempt in range(retries + 1):
        try:
            candidate = provider.complete_structured(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=_SYSTEM_PROMPT,
                schema=schema,
                timeout=timeout,
            )
        except Exception:
            logger.warning(
                "Question generation failed for %s (attempt %s)", behaviour, attempt + 1,
            )
            continue

        problems = validate_question(question=candidate)
        if not problems:
            candidate["source"] = "generated"
            return candidate

        logger.info(
            "Rejected generated %s question (attempt %s): %s",
            behaviour, attempt + 1, "; ".join(problems),
        )

    return _fallback(behaviour=behaviour)


def _fallback(*, behaviour: str) -> dict:
    banked = fallback_for(behaviour=behaviour)
    if banked is None:
        msg = f"No generated or banked question available for {behaviour!r}"
        raise LookupError(msg)

    logger.warning("Serving banked question for %s", behaviour)
    return {**banked, "source": "fallback"}


_SYSTEM_PROMPT = (
    "You write onboarding questions for Belong, an investment app in Kenya.\n\n"
    "Write the way a thoughtful person asks a friend what they want for their "
    "money — curious, warm, direct, never clinical. Someone answering should "
    "feel talked to, not assessed. They will never know a scale exists.\n\n"
    "You are a phrasing engine, not a scorer. You never decide what kind of "
    "investor someone is. You write one short multiple-choice question and "
    "declare, for each option, which anchor on our fixed scale that option "
    "represents.\n\n"
    "Rules:\n"
    "- Plain conversational English. No financial jargon.\n"
    "- The anchor definitions we give you are internal. Never echo their "
    "wording, and never let their clinical tone leak into what you write.\n"
    "- Options must be things a real person would say about themselves, out "
    "loud, in their own words.\n"
    "- Never promise, imply, or quote a return. Never name a product.\n"
    "- Never describe any investment as safe, guaranteed, or risk-free.\n"
    "- Each option must sit at a different anchor, and together they must "
    "span most of the scale — otherwise the question measures nothing.\n\n"
    "Sounding human is a requirement, not a preference. A question that "
    "measures correctly but reads like a form has failed."
)
