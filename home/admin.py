from django import forms
from django.contrib import admin
from users.models import Profile
from .models import GM, Point, WgUpdate, LdapGroup, Role, Room


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
        (None, {'fields': ['number', 'date_conv']}),
    ]
    inlines = [PointInline, WgUpdateInline]
    list_display = ('number', 'date_conv', 'discussions', 'proposals')

# list_display = ('title', 'proposal')
# list_filter = ['pub_date']
# search_fields = ['question_text']


class RoleAdmin(admin.ModelAdmin):
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
        (None,
         {'fields': ['role_name', 'assigned_to', 'past_holders', 'group', 'subgroup',
                     'description', 'permissions', 'ldap_groups']})
    ]
    list_display = ('role_name', 'members', 'group')
    search_fields = ['role_name']
    autocomplete_fields = ['assigned_to', 'past_holders', 'ldap_groups']


class LdapAdmin(admin.ModelAdmin):
    search_fields = ['ldap_cn']

class MapSelectionForm(forms.ModelForm):
    fields = ['current_occupant']
    def __init__(self, *args, **kwargs):
        super(MapSelectionForm, self).__init__(*args, **kwargs)
        self.fields['current_occupant'].queryset = Profile.objects.filter(current_member=True)

class MapAdmin(admin.ModelAdmin):
    form = MapSelectionForm



admin.site.register(GM, GMAdmin)
admin.site.register(LdapGroup, LdapAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Room, MapAdmin)
