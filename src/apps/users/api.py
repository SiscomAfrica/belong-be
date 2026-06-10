from __future__ import annotations

from uuid import UUID

from ninja import Router

from apps.users.schemas import (
    DeviceOut,
    DeviceRegisterIn,
    TermsAcceptIn,
    UserOut,
    UserUpdateIn,
)
from apps.users.selectors.get_user_devices import get_user_devices
from apps.users.services.accept_terms import accept_terms
from apps.users.services.register_device import deactivate_device, register_device
from apps.users.services.update_profile import update_profile

users_router = Router(tags=["users"])


@users_router.get("/me", response=UserOut)
def me(request):  # noqa: ANN001, ANN201
    """Return the authenticated user's profile."""
    return request.auth


@users_router.patch("/me", response=UserOut)
def update_me(request, payload: UserUpdateIn):  # noqa: ANN001, ANN201
    """Update the authenticated user's profile fields."""
    return update_profile(user=request.auth, **payload.dict(exclude_unset=True))


@users_router.post("/me/terms", response=UserOut)
def accept(request, payload: TermsAcceptIn):  # noqa: ANN001, ANN201
    """Accept the current terms and conditions."""
    return accept_terms(user=request.auth, accepted=payload.accepted)


@users_router.post("/me/devices", response={201: DeviceOut})
def add_device(request, payload: DeviceRegisterIn):  # noqa: ANN001, ANN201
    """Register a new device for push notifications."""
    device = register_device(user=request.auth, **payload.dict())
    return 201, device


@users_router.get("/me/devices", response=list[DeviceOut])
def list_devices(request):  # noqa: ANN001, ANN201
    """List all registered devices for the authenticated user."""
    return get_user_devices(user=request.auth)


@users_router.delete("/me/devices/{device_id}", response={204: None})
def remove_device(request, device_id: UUID):  # noqa: ANN001, ANN201
    """Deactivate and remove a registered device."""
    deactivate_device(user=request.auth, device_pk=device_id)
    return 204, None
