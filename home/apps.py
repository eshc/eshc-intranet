from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class MyAdminConfig(AdminConfig):
    default_site = 'home.auth.MyAdminSite'


class HomeConfig(AppConfig):
    name = 'home'
    verbose_name = 'Misc co-op things'

    def ready(self):
        import home.signals
