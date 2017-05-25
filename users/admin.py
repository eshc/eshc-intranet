from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from users.models import Profile

admin.site.unregister(User)

class ProfileInLine(admin.StackedInline):
	model = Profile
	can_delete = False

class UserProfileAdmin(UserAdmin):
	inlines = [ ProfileInLine, ]

	def ref_number(self, obj):
		try:
			return obj.profile.ref_number
		except Profile.DoesNotExist:
			return ''

	list_display = UserAdmin.list_display + ('ref_number', )

admin.site.register(User, UserProfileAdmin)
