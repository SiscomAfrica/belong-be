from __future__ import annotations

import environ

env = environ.Env()

SMS_API_KEY = env("SMS_API_KEY", default="")
SMS_SERVICE_ID = env("SMS_SERVICE_ID", default="0")
SMS_SHORTCODE = env("SMS_SHORTCODE", default="SISCOM TECH")
SMS_ENABLED = env.bool("SMS_ENABLED", default=False)
