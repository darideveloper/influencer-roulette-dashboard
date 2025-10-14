from django.contrib import admin
from roulette import models

@admin.register(models.Roulette)
class RouletteAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "logo", "subtitle", "bottom_text", "bg_image", "current_spins", "wrong_icon", "message_error_no_spin", "message_lose_lose", "message_win", "color_spin_1", "color_spin_2", "color_spin_3", "color_spin_4", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "slug", "logo", "subtitle", "bottom_text", "bg_image", "current_spins", "wrong_icon", "message_error_no_spin", "message_lose_lose", "message_win", "color_spin_1", "color_spin_2", "color_spin_3", "color_spin_4")
    readonly_fields = ("created_at", "updated_at")

@admin.register(models.Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "min_spins", "image", "active", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description", "min_spins", "image", "active")

@admin.register(models.Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "last_spin", "last_extra_spin", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "email", "last_spin", "last_extra_spin")
    readonly_fields = ("created_at", "updated_at")

@admin.register(models.ParticipantAward)
class ParticipantAwardAdmin(admin.ModelAdmin):
    list_display = ("participant", "award", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("participant", "award")
    readonly_fields = ("created_at", "updated_at")