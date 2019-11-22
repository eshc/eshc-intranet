from django.contrib import admin
from .models import FinanceConfig


@admin.register(FinanceConfig)
class FinanceAdmin(admin.ModelAdmin):
    actions = None
    fields = ('monthlyRent',)

    def has_add_permission(self, _request):
        return False

    def has_delete_permission(self, _request, _obj=None):
        return False
