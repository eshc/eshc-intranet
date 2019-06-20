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
        fields = (
        'first_name', 'last_name', 'email', 'profile__ref_number', 'profile__current_member', 'profile__share_received',
        'username')


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

    def current_member(self, obj):
        try:
            return obj.profile.current_member
        except Profile.DoesNotExist:
            return ''

    share_received.boolean = True
    current_member.boolean = True
    list_display = BaseUserAdmin.list_display + ('ref_number', 'current_member', 'share_received', 'is_active')
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def action_mark_members_current(self, request, queryset):
        rows_updated = 0
        for usr in queryset.select_related('profile'):
            rows_updated += 1
            usr.profile.current_member = True
            usr.profile.save()
            usr.is_active = True
            usr.save()
        self.message_user(request, '%s member(s) marked as currently residing and active' % (rows_updated,))
    action_mark_members_current.short_description = 'Mark selected members as currently residing and active'

    def action_mark_members_left(self, request, queryset):
        rows_updated = 0
        for usr in queryset.select_related('profile'):
            rows_updated += 1
            usr.profile.current_member = False
            usr.profile.save()
            usr.is_active = False
            usr.save()
        self.message_user(request, '%s member(s) marked as having left the co-op and inactive' % (rows_updated,))
    action_mark_members_left.short_description = 'Mark selected members as having left the co-op and inactive'

    def action_give_share(self, request, queryset):
        rows_updated = 0
        for usr in queryset.select_related('profile'):
            rows_updated += 1
            usr.profile.share_received = True
            usr.profile.save()
        self.message_user(request, '%s member(s) marked as having paid the share' % (rows_updated,))
    action_give_share.short_description = 'Mark selected members as having paid the share'

    def action_remove_share(self, request, queryset):
        rows_updated = 0
        for usr in queryset.select_related('profile'):
            rows_updated += 1
            usr.profile.share_received = False
            usr.profile.save()
        self.message_user(request, '%s members\' share removed' % (rows_updated,))

    action_remove_share.short_description = 'Remove selected members\' share paid status'

    actions = ['action_mark_members_current', 'action_mark_members_left',
               'action_give_share', 'action_remove_share']


admin.site.register(User, UserAdmin)
