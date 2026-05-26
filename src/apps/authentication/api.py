from __future__ import annotations

from ninja import Router

from apps.authentication.schemas import (
    AuthTokenOut,
    BiometricsEnableIn,
    OTPSendIn,
    OTPSentOut,
    OTPVerifyIn,
    PINSetIn,
    PINVerifyIn,
    RegisterIn,
)
from apps.authentication.services.enable_biometrics import enable_biometrics
from apps.authentication.services.register import register
from apps.authentication.services.send_otp import send_otp
from apps.authentication.services.set_pin import set_pin
from apps.authentication.services.verify_otp import verify_otp
from apps.authentication.services.verify_pin import verify_pin
from apps.users.schemas import UserOut

auth_router = Router(tags=["auth"])


@auth_router.post("/register", response={201: AuthTokenOut}, auth=None)
def register_user(request, payload: RegisterIn):
    tokens = register(
        phone=payload.phone,
        otp_code=payload.otp_code,
        pin=payload.pin,
        referred_by_code=payload.referred_by_code,
    )
    return 201, tokens


@auth_router.post("/otp/send", response=OTPSentOut, auth=None)
def send_otp_endpoint(request, payload: OTPSendIn):
    send_otp(phone=payload.phone, purpose=payload.purpose, channel=payload.channel)
    return OTPSentOut(message="OTP sent successfully")


@auth_router.post("/otp/verify", response={200: dict}, auth=None)
def verify_otp_endpoint(request, payload: OTPVerifyIn):
    verify_otp(phone=payload.phone, code=payload.code, purpose=payload.purpose)
    return {"verified": True}


@auth_router.post("/pin/set", response=UserOut)
def set_pin_endpoint(request, payload: PINSetIn):
    return set_pin(user=request.auth, pin=payload.pin)


@auth_router.post("/pin/verify", response={200: dict})
def verify_pin_endpoint(request, payload: PINVerifyIn):
    verify_pin(user=request.auth, pin=payload.pin)
    return {"verified": True}


@auth_router.post("/biometrics/enable", response=UserOut)
def enable_biometrics_endpoint(request, payload: BiometricsEnableIn):
    return enable_biometrics(user=request.auth, enable=payload.enable)
