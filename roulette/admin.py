from django.contrib import admin
from roulette import models


@admin.register(models.TestOther)
class TestOtherAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(models.Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at", "test_other", "client")
    search_fields = ("name", "client__name", "client__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "address", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
