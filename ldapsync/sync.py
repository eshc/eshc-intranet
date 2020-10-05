from base64 import b64encode
from ldap3 import *
from eshcIntranet.settings import *
from leases.models import Lease
from users.models import User, Profile
from home.models import Role, LdapGroup
from typing import Callable, Dict, Union, Set
from datetime import date


def find_lease_for_profile(u: Profile) -> Union[None, Lease]:
    now = date.today()
    try:
        return Lease.objects.filter(user=u.user, start_date__lte=now, end_date__gte=now).latest('start_date')
    except Lease.DoesNotExist:
        return None


def lease_to_room_number(l: Lease) -> str:
    if l is None:
        return '0/0Z'
    else:
        return '%s/%s%s' % (l.building, l.flat, l.room)


def intranet_to_ldap_password(p: str) -> str:
    if not p.startswith('pbkdf2_sha256$'):
        return p
    parts = p.split('$')
    iters = parts[1]
    salt = parts[2]
    bdk = parts[3].replace('+', '.').rstrip('=')
    b64salt = b64encode(salt.encode('utf-8')).decode('utf-8').rstrip('=')
    return '{PBKDF2-SHA256}%s$%s$%s' % (iters, b64salt, bdk)


def user_roles_string(u: User) -> str:
    qs = Role.objects.filter(assigned_to=u)
    roles = ", ".join(map(lambda r: r.role_name, qs))
    if len(roles) == 0:
        return "No role assigned"
    else:
        return roles


LDAP_ATTR_MAP: Dict[str, Callable[[Profile], str]] = {
    # LDAP Name : lambda (Profile)->value
    'cn': lambda u: u.user.get_full_name(),
    'givenName': lambda u: u.user.first_name,
    'sn': lambda u: u.user.last_name,
    'displayName': lambda u: u.preferred_name,
    'mail': lambda u: u.user.email,
    'roomNumber': lambda u: lease_to_room_number(find_lease_for_profile(u)),
    'postalAddress': lambda u: u.perm_address,
    'userPassword': lambda u: intranet_to_ldap_password(u.user.password),
    'employeeNumber': lambda u: str(u.user.pk),
    'description': lambda u: user_roles_string(u.user)
}


class IntranetLdapSync:
    connection = None
    members_group = 'cn=AllMembers,ou=Groups,%s' % (LDAP_SERVER_ROOT_DN,)
    members_dn = 'ou=Members,%s' % (LDAP_SERVER_ROOT_DN,)
    exmembers_dn = 'ou=DeactivatedMembers,%s' % (LDAP_SERVER_ROOT_DN,)
    empty_group_member = 'uid=groupfiller,%s' % (LDAP_SERVER_ROOT_DN,)
    mock = False

    filter_member = '(objectclass=inetOrgPerson)'

    def __init__(self):
        self.connection = Connection(LDAP_SERVER_ADDR, user=LDAP_SERVER_AUTH_USER,
                                     password=LDAP_SERVER_AUTH_PASSWORD, auto_bind=True)

    def __unsync_intranet_user(self, user: User):
        """
        Move user to the LDAP ex-members group.
        """
        uid = user.pk
        u_query = '(&%s(|(uid=%s)(employeeNumber=%d)))' % (self.filter_member, user.username, uid)
        self.connection.search(self.members_dn, u_query)
        response = self.connection.response
        if len(response) < 1:
            # No entry to move, exit
            if self.mock:
                print("Not current and not existing")
            return
        if self.mock:
            print("Not current member - moving")
        for invalid in response[1:]:
            if not self.mock:
                self.connection.delete(invalid['dn'])
            else:
                print("Deleting extra (ex)member %s" % (invalid['dn'],))
        dn = response[0]['dn']
        rdn = dn.split(',')[0]
        assert 0 < len(rdn) < len(dn)
        if not self.mock:
            self.connection.modify_dn(dn, rdn, delete_old_dn=True, new_superior=self.exmembers_dn)
            if self.connection.result['result'] == 68: # Already exists
                self.connection.delete('%s,%s'%(rdn,self.exmembers_dn))
                result = self.connection.modify_dn(dn, rdn, delete_old_dn=True, new_superior=self.exmembers_dn)
                if not result:
                    print(self.connection.result)
        else:
            print("Move now-ex user ", dn, " to ", rdn, ",", self.exmembers_dn)
        pass

    def __create_intranet_user(self, user: User):
        """
        Create user in LDAP when they're missing
        """
        profile = user.profile
        assert profile
        uid = user.pk
        obj_classes = ['inetOrgPerson', 'Nextcloud']
        new_attrs = {'NextcloudQuota': '1GB'}
        for ldap_attr, mapfn in LDAP_ATTR_MAP.items():
            real_value = type(mapfn) == str and mapfn or mapfn(profile)
            if len(real_value) > 0:
                new_attrs[ldap_attr] = real_value
                if self.mock:
                    print("Adding field %s: '%s'" % (ldap_attr, real_value))
        dn = 'uid=%s,%s' % (user.username, self.members_dn)
        if not self.mock:
            succ = self.connection.add(dn, obj_classes, new_attrs)
            assert succ
        else:
            print("Adding DN: %s" % (dn,))

    def sync_intranet_user(self, user: User):
        """
        Ensure data for user is up-to-date (active or non-active respectively)

        Guarantee: at the end if the user is active, they get a single LDAP account or their account gets moved
        to ex-members group if that's not the case
        """
        if self.mock:
            print(" * Mocking ldap sync for user %s (%s)" % (user.username, user.get_full_name()))
        # User+Profile basic data synchronization
        profile = user.profile
        assert profile
        if not profile.current_member:
            self.__unsync_intranet_user(user)
            return

        assert profile.current_member
        uid = user.pk
        u_query = '(&%s(|(uid=%s)(employeeNumber=%d)))' % (self.filter_member, user.username, uid)
        self.connection.search(self.members_dn, u_query)
        response = self.connection.response
        found_users = len(response)
        assert found_users >= 0
        if found_users == 0:
            # No user found, check if a re-activated member?
            self.connection.search(self.exmembers_dn, u_query)
            response = self.connection.response
            found_exusers = len(response)
            assert found_exusers >= 0
            if found_exusers == 0:
                if self.mock:
                    print("Create new user for ", user.get_full_name(), ":", user.get_username())
                # Make new user
                self.__create_intranet_user(user)
                # Continue, as groups need to be synced too
                pass
            elif found_exusers > 1:
                # More than 1 user => this is an invalid state, just pick the first one and delete the rest
                for invalid_resp in response[1:]:
                    if not self.mock:
                        succ = self.connection.delete(invalid_resp['dn'])
                        assert succ
                    else:
                        print("Delete extra ex-user ", invalid_resp['dn'])
                found_exusers = 1
            if found_exusers == 1:
                # Move user into active members and continue resyncing
                dn: str = response[0]['dn']
                rdn = dn.split(',')[0]
                assert 0 < len(rdn) < len(dn)
                if not self.mock:
                    succ = self.connection.modify_dn(dn, rdn, delete_old_dn=True, new_superior=self.members_dn)
                    assert succ
                else:
                    print("Move not-ex-user ", dn, " to ", rdn, ",", self.members_dn)
                pass
        elif found_users > 1:
            # More than 1 user => invalid state, pick first one and delete the rest
            for invalid_resp in response[1:]:
                if not self.mock:
                    succ = self.connection.delete(invalid_resp['dn'])
                    assert succ
                else:
                    print("Delete extra user ", invalid_resp['dn'])
            pass
        else:
            if self.mock:
                print("A single LDAP user existing: " + response[0]['dn'])

        # 1 user in the members group to synchronize
        self.connection.search(self.members_dn,
                               u_query,
                               attributes=list(LDAP_ATTR_MAP.keys()) + ["memberOf"])
        response = self.connection.response
        if not self.mock:
            assert len(response) == 1
        else:
            if len(response) < 1:
                response = [{'dn': 'uid=%s,%s' % (user.username, self.members_dn), 'attributes': {}}]
        ldap_response = response[0]
        user_dn = ldap_response['dn']
        # Sync attributes
        attr_changes = {}
        num_changes = 0
        for ldap_attr, mapfn in LDAP_ATTR_MAP.items():
            real_value = type(mapfn) == str and mapfn or mapfn(profile)
            ldap_value = ldap_response['attributes'].get(ldap_attr, [])
            if type(ldap_value) == list:
                ldap_value = len(ldap_value) == 1 and ldap_value[0] or ''
            if type(ldap_value) == bytes:
                ldap_value = ldap_value.decode('utf-8')
            if real_value != ldap_value:
                attr_changes[ldap_attr] = [(MODIFY_REPLACE, [real_value])]
                if self.mock:
                    print("Updating field %s: '%s'->'%s'" % (ldap_attr, ldap_value, real_value))
                num_changes += 1
        if num_changes > 0:
            if not self.mock:
                succ = self.connection.modify(user_dn, attr_changes)
                assert succ
            else:
                print("Changing %d fields for dn %s" % (num_changes, user_dn))

    def __fill_ldap_group(self, group_cn: str, uids: Set[str]):
        if self.mock:
            print(" * Mocking group update:", group_cn)
        ldap_uids = set()
        self.connection.search(group_cn, '(cn=*)', BASE, attributes=['member'])
        response = self.connection.response[0]
        has_empty = False
        to_remove_ex = set()
        for ldn in response['attributes']['member']:
            if ldn != self.empty_group_member:
                if ldn.endswith(self.exmembers_dn):
                    to_remove_ex.add(ldn)
                else:
                    ldap_uids.add(ldn.split(',')[0][4:])
            else:
                has_empty = True
        to_remove = ldap_uids - uids
        to_add = uids - ldap_uids
        modifications = []
        for uid in to_add:
            modifications.append((MODIFY_ADD, 'uid=%s,%s' % (uid, self.members_dn)))
        if not has_empty:
            modifications.append((MODIFY_ADD, self.empty_group_member))
        for uid in to_remove:
            modifications.append((MODIFY_DELETE, 'uid=%s,%s' % (uid, self.members_dn)))
        for dn in to_remove_ex:
            modifications.append((MODIFY_DELETE, dn))
        if self.mock:
            print(modifications)
        else:
            if len(modifications) > 0:
                self.connection.modify(group_cn, {'member': modifications})
        pass

    def sync_intranet_ldap_group(self, group: LdapGroup):
        uids = set()
        for p in Profile.objects.filter(extra_ldap_groups=group, current_member=True):
            uids.add(p.user.username)
        for r in Role.objects.filter(ldap_groups=group):
            for u in r.assigned_to.filter(profile__current_member=True):
                if u.username not in uids:
                    uids.add(u.username)
        self.__fill_ldap_group(group.ldap_cn, uids)

    def sync_all_ldap_groups(self):
        for g in LdapGroup.objects.all():
            self.sync_intranet_ldap_group(g)
        uids = set()
        for u in User.objects.filter(profile__current_member=True):
            uids.add(u.username)
        self.__fill_ldap_group(self.members_group, uids)
