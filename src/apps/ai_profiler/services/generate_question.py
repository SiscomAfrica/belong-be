from __future__ import annotations

import logging

from django.conf import settings

from apps.ai_profiler.exceptions import ProviderRateLimitedError
from apps.ai_profiler.providers import get_llm_provider
from apps.ai_profiler.services.fallback_questions import fallback_for
from apps.ai_profiler.services.question_prompt import build_generation_prompt
from apps.ai_profiler.services.question_schema import question_schema
from apps.ai_profiler.services.question_system_prompt import SYSTEM_PROMPT
from apps.ai_profiler.services.validate_question import validate_question

logger = logging.getLogger(__name__)


def generate_question(*, behaviour: str, asked: list[dict] | None = None) -> dict:
    """Produce one validated question targeting `behaviour`.

    Retries on invalid output, then falls back to the banked question, so a
    generation failure never leaves the caller empty-handed.

    The one thing it does not absorb is a rate limit: that is raised, because
    the right response is to stop rather than to substitute. Both callers are
    background work — the pool refill and the check_llm command — so nobody is
    waiting on this. The request path stopped calling it when next_question
    was made to serve the bank instead.
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
                system_prompt=SYSTEM_PROMPT,
                schema=schema,
                timeout=timeout,
            )
        except ProviderRateLimitedError:
            # Not worth a second attempt: the provider has said no for a
            # while, and two more immediate calls only confirm it.
            logger.warning("Provider rate limited generating %s", behaviour)
            raise
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
