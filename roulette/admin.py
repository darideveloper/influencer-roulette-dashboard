from django.contrib import admin
from roulette import models


@admin.register(models.Roulette)
class RouletteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "subtitle",
        "spins_space_hours",
        "spins_ads_limit",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = (
        "name",
        "subtitle",
        "bottom_text",
        "message_no_spins",
        "message_lose",
        "message_win",
    )
    readonly_fields = ("slug", "created_at", "updated_at")


@admin.register(models.Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "roulette",
        "description",
        "active",
        "created_at",
        "updated_at",
    )
    list_filter = ("roulette", "active", "created_at", "updated_at")
    search_fields = ("name", "description")


@admin.register(models.Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.ParticipantSpin)
class ParticipantSpinAdmin(admin.ModelAdmin):
    list_display = (
        "participant",
        "roulette",
        "is_extra_spin",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "participant",
        "roulette",
        "is_extra_spin",
        "created_at",
        "updated_at",
    )
    search_fields = ("participant__name", "participant__email", "roulette__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.ParticipantAward)
class ParticipantAwardAdmin(admin.ModelAdmin):
    list_display = ("participant", "award", "created_at", "updated_at")
    list_filter = ("participant", "award__roulette", "created_at", "updated_at")
    search_fields = (
        "participant__name",
        "participant__email",
        "award__name",
        "award__roulette__name",
    )
    readonly_fields = ("created_at", "updated_at")
