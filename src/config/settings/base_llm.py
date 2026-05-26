from __future__ import annotations

import environ

env = environ.Env()

LLM_PROVIDER = env("LLM_PROVIDER", default="claude")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
ANTHROPIC_MODEL = env("ANTHROPIC_MODEL", default="claude-sonnet-4-20250514")
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o")
