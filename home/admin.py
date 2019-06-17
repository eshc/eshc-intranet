from django.contrib import admin
from django.contrib.auth.models import User
from .models import GM, Point, WgUpdate, LdapGroup, Role


class PointInline(admin.TabularInline):
	model = Point
	fieldsets = []
	extra = 1

class WgUpdateInline(admin.TabularInline):
	model = WgUpdate
	fieldsets = []
	extra = 1

class GMAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,		{'fields': ['number', 'date_conv']}),
		]
	inlines = [PointInline, WgUpdateInline]
	list_display = ('number','date_conv','discussions', 'proposals')

	# list_display = ('title', 'proposal')
	# list_filter = ['pub_date']
	# search_fields = ['question_text']


class RoleAdmin(admin.ModelAdmin):
	readonly_fields = ('all_members',)
	def member(self, obj):
		try:
			return obj.assigned_to.first_name + ' ' + obj.assigned_to.last_name
		except:
			return 'NOT ASSIGNED'

	def all_members(self, obj):
		users = User.objects.filter(is_active=True)
		extracted = [u.get_full_name()+'________USERNAME:'+u.username for u in users]
		return '\n'.join(extracted)

	fieldsets = [
		(None,	{'fields': ['role_name', 'assigned_to', 'group', 'subgroup', 'description', 'ldap_groups']}),
		('Use the', {'fields': [readonly_fields,]})
		] 
	list_display = ('role_name', 'member', 'group')

admin.site.register(GM, GMAdmin)
admin.site.register(LdapGroup)
admin.site.register(Role, RoleAdmin)
