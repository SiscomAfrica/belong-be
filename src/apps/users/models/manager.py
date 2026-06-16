from __future__ import annotations

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager for phone-based User model."""

    def create_user(
        self,
        phone: str,
        password: str | None = None,
        **extra_fields,
    ):
        if not phone:
            raise ValueError("Phone number is required")
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("username", phone)
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        phone: str,
        password: str | None = None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra_fields)
