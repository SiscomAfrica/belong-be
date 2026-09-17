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

# M-Pesa Ratiba (standing orders) — automated recurring deductions.
#
# Ratiba runs on the same Daraja host and OAuth credentials as STK push, so it
# reuses MPESA_CONSUMER_KEY/SECRET and MPESA_ENV. What it does NOT share is
# go-live: Ratiba needs a signed commercial agreement with Safaricom on top of
# the usual shortcode approval, so this stays off until that is in place.
# With it off, recurring plans keep running on the wallet-sweep path alone.
MPESA_RATIBA_ENABLED = env.bool("MPESA_RATIBA_ENABLED", default=False)

# Paybill that collects the deductions. Defaults to the STK shortcode because
# that is the common case, but Ratiba can collect to a different one.
MPESA_RATIBA_SHORTCODE = env("MPESA_RATIBA_SHORTCODE", default=MPESA_SHORTCODE)

# "4" = PayBill, "2" = Till. Drives ReceiverPartyIdentifierType and the
# matching TransactionType on the create request.
MPESA_RATIBA_RECEIVER_TYPE = env("MPESA_RATIBA_RECEIVER_TYPE", default="4")

# How long a standing order runs before Safaricom stops it. Ratiba requires an
# explicit EndDate, so an open-ended plan needs a horizon picked for it; the
# plan is renewed from our side well before this lapses.
MPESA_RATIBA_DURATION_DAYS = env.int("MPESA_RATIBA_DURATION_DAYS", default=730)
