from base64 import b64encode
from django.db.models import Model
from ldap3 import *
from eshcIntranet.settings import *
from leases.models import Lease
from users.models import User, Profile, LdapGroup
from typing import Callable, Dict
from datetime import date


def findLeaseForProfile(u: Profile) -> Lease:
    now = date.today()
    try:
        return Lease.objects.filter(user=u.user, start_date__lte=now, end_date__gte=now).latest('start_date')
    except Model.DoesNotExist:
        return None


def leaseToRoomNumber(l: Lease) -> str:
    if l == None:
        return '0/0Z'
    else:
        return '%s/%s%s' % (l.building, l.flat, l.room)


def intranetToLDAPPassword(p: str) -> str:
    if not p.startswith('pbkdf2_sha256$'):
        return p
    parts = p.split('$')
    iters = parts[1]
    salt = parts[2]
    bdk = parts[3].replace('+', '.').rstrip('=')
    b64salt = b64encode(salt.encode('utf-8')).decode('utf-8').rstrip('=')
    return '{PBKDF2-SHA256}%s$%s$%s' % (iters, b64salt, bdk)


LDAP_ATTR_MAP: Dict[str, Callable[[Profile], str]] = {
    # LDAP Name : lambda (Profile)->value
    'cn': lambda u: u.user.get_full_name(),
    'givenName': lambda u: u.user.first_name,
    'sn': lambda u: u.user.last_name,
    'displayName': lambda u: u.preferred_name,
    'mail': lambda u: u.user.email,
    'roomNumber': lambda u: leaseToRoomNumber(findLeaseForProfile(u)),
    'postalAddress': lambda u: u.perm_address,
    'telephoneNumber': lambda u: u.phone_number,
    'userPassword': lambda u: intranetToLDAPPassword(u.user.password),
    'employeeNumber': lambda u: str(u.user.pk)
}


class IntranetLdapSync:
    connection = None
    members_dn = 'ou=Members,%s'%(LDAP_SERVER_ROOT_DN,)
    exmembers_dn = 'ou=DeactivatedMembers,%s' % (LDAP_SERVER_ROOT_DN,)

    filter_member = '(objectclass=inetOrgPerson)'

    def __init__(self):
        self.connection = Connection(LDAP_SERVER_ADDR, user=LDAP_SERVER_AUTH_USER,
                                     password=LDAP_SERVER_AUTH_PASSWORD, auto_bind=True)

    def queryAllMembers(self):
        return self.connection.search(self.members_dn, self.filter_member)