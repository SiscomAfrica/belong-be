from __future__ import annotations

from django.contrib import admin

from apps.wishlist.models import WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "fund", "created_at")
    search_fields = ("user__phone", "fund__name")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
