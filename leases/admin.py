from django.contrib import admin

from .models import Lease

class LeaseAdmin(admin.ModelAdmin):
	list_display = ['start_date', 'end_date', 'lease_type']

	def member(self, obj):
		try:
			return obj.user.first_name + ' ' + obj.user.last_name
		except Profile.DoesNotExist:
			return ''

	list_display = list_display + ['member']

admin.site.register(Lease, LeaseAdmin)
