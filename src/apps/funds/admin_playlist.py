from __future__ import annotations

from django.contrib import admin

from apps.common.admin_mixins import HeroImageAdminMixin
from apps.funds.models import Playlist, PlaylistFund


class PlaylistFundInline(admin.TabularInline):
    model = PlaylistFund
    extra = 1
    autocomplete_fields = ("fund",)
    ordering = ("position",)


@admin.register(Playlist)
class PlaylistAdmin(HeroImageAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "hero_image_preview", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("hero_image_preview",)
    inlines = [PlaylistFundInline]
    ordering = ("name",)
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "is_active")}),
        ("Hero Image", {"fields": (
            "hero_image", "hero_image_url", "hero_image_preview",
        )}),
    )
