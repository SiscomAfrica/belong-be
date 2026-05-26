from __future__ import annotations

from ninja import Schema


class RegisterIn(Schema):
    phone: str
    otp_code: str
    pin: str
    referred_by_code: str = ""


class OTPSendIn(Schema):
    phone: str
    purpose: str = "REGISTER"
    channel: str = "SMS"


class OTPVerifyIn(Schema):
    phone: str
    code: str
    purpose: str = "REGISTER"


class PINSetIn(Schema):
    pin: str


class PINVerifyIn(Schema):
    pin: str


class BiometricsEnableIn(Schema):
    enable: bool = True
