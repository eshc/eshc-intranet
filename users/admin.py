from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


from users.models import Profile
from leases.models import Lease
from import_export import resources
from import_export.admin import ImportExportModelAdmin


admin.site.unregister(User)

class ProfileInLine(admin.StackedInline):
	model = Profile
	can_delete = False

class LeaseInLine(admin.StackedInline):
	model = Lease
	extra = 0

class UserResource(resources.ModelResource):

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email','profile__ref_number', 'profile__share_received', 'username')

# class UserAdmin(BaseUserAdmin):
class UserAdmin(ImportExportModelAdmin):
	resource_class = UserResource
	inlines = [LeaseInLine, ProfileInLine, ]

	def ref_number(self, obj):
		try:
			return obj.profile.ref_number
		except Profile.DoesNotExist:
			return ''

	def share_received(self, obj):
		try:
			return obj.profile.share_received
		except Profile.DoesNotExist:
			return ''

	def active(self, obj):
		try:
			return obj.profile.is_active
		except Profile.DoesNotExist:
			return ''

	def extra_ldap_groups(self, obj):
		try:
			return obj.profile.ref_number
		except Profile.DoesNotExist:
			return ''
			
	share_received.boolean = True
	list_display = BaseUserAdmin.list_display + ('ref_number', 'share_received', 'is_active')



admin.site.register(User, UserAdmin)
