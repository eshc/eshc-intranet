from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from users.models import User, Profile
from home.models import Role, LdapGroup
from ldapsync.sync import IntranetLdapSync


@receiver(post_save, dispatch_uid='ldap_sync_on_save')
@receiver(m2m_changed, dispatch_uid='ldap_sync_m2m_save')
def ldap_sync_on_save(sender, **kwargs):
    if (sender is not User
            and sender is not Profile
            and sender is not Role
            and sender is not LdapGroup
            and sender is not Profile.extra_ldap_groups.through
            and sender is not Role.ldap_groups.through
            and sender is not Role.assigned_to.through):
        return
    user = None
    if sender is User:
        user = kwargs['instance']
    if sender is Profile:
        user = kwargs['instance'].user
    try:
        ils = IntranetLdapSync()
        if user is not None:
            ils.sync_intranet_user(user)
        ils.sync_all_ldap_groups()
        del ils
    except:
        print("Error occured on LDAP sync")
    else:
        print("LDAP sync OK")
