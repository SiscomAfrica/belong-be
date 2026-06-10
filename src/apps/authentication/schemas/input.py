from __future__ import annotations

from ninja import Schema
from pydantic import Field


class RegisterIn(Schema):
    phone: str = Field(description="E.164 phone number")
    otp_code: str = Field(description="6-digit OTP received via SMS")
    pin: str = Field(description="4-digit numeric PIN")
    referred_by_code: str = Field(default="", description="Referral code of inviting user")


class OTPSendIn(Schema):
    phone: str = Field(description="E.164 phone number")
    purpose: str = Field(default="REGISTER", description="OTP purpose: REGISTER | LOGIN | RESET_PIN")
    channel: str = Field(default="SMS", description="Delivery channel: SMS | WHATSAPP")


class OTPVerifyIn(Schema):
    phone: str = Field(description="E.164 phone number used when requesting OTP")
    code: str = Field(description="6-digit OTP code to verify")
    purpose: str = Field(default="REGISTER", description="Must match the purpose used in send")


class PINSetIn(Schema):
    pin: str = Field(description="4-digit numeric PIN to set")


class PINVerifyIn(Schema):
    pin: str = Field(description="4-digit numeric PIN to verify")


class LoginIn(Schema):
    phone: str = Field(description="E.164 phone number")
    pin: str = Field(description="4-digit numeric PIN")


class BiometricsEnableIn(Schema):
    enable: bool = Field(default=True, description="True to enable biometrics, false to disable")
