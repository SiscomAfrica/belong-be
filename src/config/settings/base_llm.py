from __future__ import annotations

import environ

env = environ.Env()

LLM_PROVIDER = env("LLM_PROVIDER", default="claude")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
ANTHROPIC_MODEL = env("ANTHROPIC_MODEL", default="claude-sonnet-5")
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o")
GROQ_API_KEY = env("GROQ_API_KEY", default="")
GROQ_MODEL = env("GROQ_MODEL", default="openai/gpt-oss-120b")

# Question generation runs while the user is answering the previous question,
# so it gets a tighter budget than conversational replies. Blowing it falls
# back to the vetted question bank rather than showing a spinner.
LLM_GENERATION_TIMEOUT = env.int("LLM_GENERATION_TIMEOUT", default=20)
LLM_GENERATION_RETRIES = env.int("LLM_GENERATION_RETRIES", default=2)
