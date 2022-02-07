from django.contrib import admin

from .models import Lease, Covid, Inventory
from import_export.admin import ImportExportModelAdmin

class InventoryInline(admin.TabularInline):
	model = Inventory
	
class LeaseAdmin(admin.ModelAdmin):
	list_display = ['start_date', 'end_date', 'lease_type']

	def member(self, obj):
		try:
			return obj.user.first_name + ' ' + obj.user.last_name
		except Profile.DoesNotExist:
			return ''
	inlines = [InventoryInline]

	list_display = list_display + ['member']

	search_fields = ['lease_type', 'start_date', 'end_date', 'user__first_name', 'user__last_name']
	autocomplete_fields = ['user']

class CovidAdmin(ImportExportModelAdmin):
	list_display = ['covid_pos_date', 'building', 'flat', 'room',]

	def member(self, obj):
		try:
			return obj.user.first_name + ' ' + obj.user.last_name
		except Profile.DoesNotExist:
			return ''

	list_display = list_display + ['member']

	search_fields = ['covid_pos_date', 'building', 'flat', 'room',]
	autocomplete_fields = ['user']

admin.site.register(Lease, LeaseAdmin)
admin.site.register(Covid, CovidAdmin)
