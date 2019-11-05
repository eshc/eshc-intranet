from django.contrib import admin
from .models import FinanceConfig

@admin.register(FinanceConfig)
class FinanceAdmin(admin.ModelAdmin):
    pass
