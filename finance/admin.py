from django.contrib import admin
from .models import FinanceConfig
from .qbo import qbo_clean_cache


@admin.register(FinanceConfig)
class FinanceAdmin(admin.ModelAdmin):
    actions = ('clean_cache',)
    fields = ('memberCount',)

    def has_add_permission(self, _request):
        return False

    def has_delete_permission(self, _request, _obj=None):
        return False

    def clean_cache(self, _request, _qs):
        qbo_clean_cache()
