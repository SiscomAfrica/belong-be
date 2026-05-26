from __future__ import annotations

import environ

env = environ.Env()

SMILE_IDENTITY_API_KEY = env("SMILE_IDENTITY_API_KEY", default="")
SMILE_IDENTITY_PARTNER_ID = env("SMILE_IDENTITY_PARTNER_ID", default="")
SMILE_IDENTITY_ENV = env("SMILE_IDENTITY_ENV", default="sandbox")
SMILE_IDENTITY_CALLBACK_URL = env("SMILE_IDENTITY_CALLBACK_URL", default="")
