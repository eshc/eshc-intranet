from django.db import models
from django.utils import timezone


class FinanceConfig(models.Model):
    """Singleton config model"""

    qboRealmId = models.BigIntegerField(verbose_name='(API) QBO Realm ID', blank=True, null=True)
    qboAccessToken = models.CharField(verbose_name='(API) QBO Access Toekn', blank=True, null=True, max_length=256)
    qboAccessTimeout = models.DateTimeField(verbose_name='(API) QBO Access Expiry', blank=True, null=True)
    qboRefreshToken = models.CharField(verbose_name='(API) QBO Refresh Token', blank=True, null=True, max_length=256)
    qboRefreshTimeout = models.DateTimeField(verbose_name='(API) QBO Refresh Expiry', blank=True, null=True)

    monthlyRent = models.DecimalField(verbose_name='Monthly rent', max_digits=8, decimal_places=2, default=300.00)

    def get_access_token(self):
        if self.qboAccessTimeout is None or self.qboAccessTimeout <= timezone.now():
            return None
        else:
            return self.qboAccessToken

    def get_refresh_token(self):
        if self.qboRefreshTimeout is None or self.qboRefreshTimeout <= timezone.now():
            return None
        else:
            return self.qboRefreshToken

    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super(FinanceConfig, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """

        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            c = cls()
            c.save()
            return c
