from django.contrib import admin

from .models import Lease, Inventory

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

admin.site.register(Lease, LeaseAdmin)
