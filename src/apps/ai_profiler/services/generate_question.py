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
    schema = question_schema(behaviour=behaviour)
    prompt = build_generation_prompt(behaviour=behaviour, asked=asked or [])
    retries = getattr(settings, "LLM_GENERATION_RETRIES", 2)
    timeout = getattr(settings, "LLM_GENERATION_TIMEOUT", 20)

    for attempt in range(retries + 1):
        try:
            candidate = get_llm_provider().complete_structured(
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
    "You are a phrasing engine, not a scorer. You never decide what kind of "
    "investor someone is. You write one short multiple-choice question and "
    "declare, for each option, which anchor on our fixed scale that option "
    "represents.\n\n"
    "Rules:\n"
    "- Plain conversational English. No financial jargon.\n"
    "- Options must be things a real person would say about themselves.\n"
    "- Never promise, imply, or quote a return. Never name a product.\n"
    "- Never describe any investment as safe, guaranteed, or risk-free.\n"
    "- Each option must sit at a different anchor, and together they must "
    "span most of the scale — otherwise the question measures nothing."
)
