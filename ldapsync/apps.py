from django.apps import AppConfig


class LdapSyncConfig(AppConfig):
    name = "ldapsync"

    def ready(self):
        pass
