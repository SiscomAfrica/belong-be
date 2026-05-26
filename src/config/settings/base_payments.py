from __future__ import annotations

import environ

env = environ.Env()

# M-Pesa (Daraja) settings
MPESA_CONSUMER_KEY = env("MPESA_CONSUMER_KEY", default="")
MPESA_CONSUMER_SECRET = env("MPESA_CONSUMER_SECRET", default="")
MPESA_PASSKEY = env("MPESA_PASSKEY", default="")
MPESA_SHORTCODE = env("MPESA_SHORTCODE", default="174379")
MPESA_ENV = env("MPESA_ENV", default="sandbox")
MPESA_CALLBACK_BASE_URL = env("MPESA_CALLBACK_BASE_URL", default="https://localhost:8000")

# Paystack settings
PAYSTACK_SECRET_KEY = env("PAYSTACK_SECRET_KEY", default="")
PAYSTACK_PUBLIC_KEY = env("PAYSTACK_PUBLIC_KEY", default="")
