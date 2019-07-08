from django.core.management.base import BaseCommand, CommandError
from ldapsync.sync import IntranetLdapSync
from users.models import User

class Command(BaseCommand):
    help = 'Mocks the ldap update of specified user(s) or all users if no user is given'
    ils = None

    def add_arguments(self, parser):
        parser.add_argument('user', nargs='*', type=str)

    def handle(self, *args, **options):
        ils = IntranetLdapSync()
        ils.mock = True
        qs = None
        if len(options['user']) == 0:
            qs = User.objects.all()
        else:
            qs = User.objects.filter(username__in=options['user'])
        for u in qs:
            ils.sync_intranet_user(u)
        self.stdout.write(" * Finished mock-syncing users")
        ils.sync_all_ldap_groups()