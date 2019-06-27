from ajax_select import register, LookupChannel
from home.models import LdapGroup

@register('ldap')
class LdapGroupLookup(LookupChannel):
    model = LdapGroup

    def get_query(self, q, request):
        return self.model.objects.filter(ldap_cn__icontains=q).order_by('ldap_cn')[:50]

