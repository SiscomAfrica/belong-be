from __future__ import annotations

import time

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.ai_profiler.exceptions import ProviderRateLimitedError
from apps.ai_profiler.rubric import BEHAVIOUR_KEYS
from apps.ai_profiler.services.generate_question import generate_question

KEY_SETTING = {
    "claude": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
}
MODEL_SETTING = {
    "claude": "ANTHROPIC_MODEL",
    "groq": "GROQ_MODEL",
    "openai": "OPENAI_MODEL",
}


class Command(BaseCommand):
    """Report which model the profiler is actually calling, and whether it works.

    Generation failure is silent by design — a failed call falls back to the
    banked questions and the user sees a perfectly good questionnaire. That is
    the right behaviour for them and the wrong behaviour for whoever is meant
    to notice the AI has been off for a fortnight. This makes it visible.
    """

    help = "Check the configured LLM provider and attempt one real generation."

    def handle(self, *args, **options) -> None:
        provider = getattr(settings, "LLM_PROVIDER", "claude")
        key_name = KEY_SETTING.get(provider, "?")
        model_name = MODEL_SETTING.get(provider, "?")
        key = getattr(settings, key_name, "")
        model = getattr(settings, model_name, "")

        self.stdout.write(f"provider : {provider}")
        self.stdout.write(f"model    : {model}  (from {model_name})")
        self.stdout.write(
            f"api key  : {'set, ' + str(len(key)) + ' chars' if key else 'NOT SET'}"
            f"  (from {key_name})",
        )

        if not key:
            self.stdout.write(
                self.style.ERROR(
                    f"\n{key_name} is empty, so every generation fails and falls "
                    "back to the six banked questions. The questionnaire still "
                    "works — it is just not being generated.",
                ),
            )

        self.stdout.write("\nattempting one generation…")
        started = time.monotonic()
        try:
            try:
                question = generate_question(behaviour=BEHAVIOUR_KEYS[0], asked=[])
            except ProviderRateLimitedError as exc:
                # The whole point of this command is to say whether the model
                # answers. "Rate limited" is an answer, and a different
                # problem from a bad key — say which.
                self.stdout.write(
                    self.style.ERROR(f"Provider is rate limiting: {exc}"),
                )
                return
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"  raised: {exc!r}"))
            return

        elapsed = (time.monotonic() - started) * 1000
        source = question.get("source")
        line = f"  source={source}  {elapsed:.0f}ms  {question.get('question')!r}"

        if source == "generated":
            self.stdout.write(self.style.SUCCESS(line))
        else:
            self.stdout.write(self.style.WARNING(line))
            self.stdout.write(
                self.style.WARNING(
                    "  Served from the bank — the model was not used.",
                ),
            )
