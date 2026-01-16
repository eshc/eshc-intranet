from typing import final
from django.contrib import admin
from .models import Lease, Inventory
from users.models import Profile


class InventoryInline(admin.TabularInline):
    model = Inventory


@final
@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ["start_date", "end_date", "lease_type"]

    def member(self, obj):
        try:
            return obj.user.first_name + " " + obj.user.last_name
        except Profile.DoesNotExist:
            return ""

    inlines = [InventoryInline]

    list_display = ["member"] + list_display

    search_fields = [
        "lease_type",
        "start_date",
        "end_date",
        "user__first_name",
        "user__last_name",
    ]
    autocomplete_fields = ["user"]
