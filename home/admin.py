from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from .models import GM, Point, WgUpdate, LdapGroup, Role
from ajax_select import make_ajax_form

# make sure lookups are loaded
import users.lookups
import home.lookups

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


class RoleAdmin(AjaxSelectAdmin):
	def members(self, obj):
		try:
			names = ''
			for u in obj.assigned_to.all():
				if len(names) > 0:
					names += ', '
				names += u.first_name + ' ' + u.last_name
			if len(names) == 0:
				return 'NOT ASSIGNED'
			return names
		except:
			return 'NOT ASSIGNED'

	fieldsets = [
		(None,	{'fields': ['role_name', 'assigned_to', 'group', 'subgroup', 'description', 'ldap_groups']})
		] 
	list_display = ('role_name', 'members', 'group')
	search_fields = ['role_name']
	form = make_ajax_form(Role, {'assigned_to':'user', 'ldap_groups':'ldap'}, show_help_text=True)

admin.site.register(GM, GMAdmin)
admin.site.register(LdapGroup)
admin.site.register(Role, RoleAdmin)
