from ajax_select import register, LookupChannel
from django.contrib.auth.models import User
from django.db.models import Value, Q
from django.db.models.functions import Concat
from users.models import Profile

@register('user')
class UsersLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        qs = self.model.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
        return qs.filter(Q(full_name__icontains=q) or Q(username__icontains=q)).order_by('full_name')[:50]

    def format_item_display(self, item):
        return u"<span class='tag'>%s %s (%s)</span>" % (item.first_name, item.last_name, item.username)

    def format_match(self, item):
        return u"<span class='tag'>%s %s (%s)</span>" % (item.first_name, item.last_name, item.username)

@register('profile')
class ProfilesLookup(LookupChannel):
    model = Profile

    def get_query(self, q, request):
        qs = self.model.objects.annotate(full_name=Concat('user__first_name', Value(' '), 'user__last_name'))
        return qs.filter(Q(full_name__icontains=q) or Q(username__icontains=q)).order_by('full_name')[:50]

    def format_item_display(self, item):
        return u"<span class='tag'>%s %s (%s)</span>" % (item.user.first_name, item.user.last_name, item.user.username)

    def format_match(self, item):
        return u"<span class='tag'>%s %s (%s)</span>" % (item.user.first_name, item.user.last_name, item.user.username)
