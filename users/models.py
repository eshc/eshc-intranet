from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from home.models import LdapGroup

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ref_number = models.CharField(
        'Bank Reference Number', max_length=8, blank=True)
    preferred_name = models.CharField(max_length=40, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    perm_address = models.TextField(max_length=500, blank=True)
    share_received = models.BooleanField(default=False)
    extra_ldap_groups = models.ManyToManyField(LdapGroup)

    def save(self, *args, **kwargs):
        if not self.preferred_name:
            self.preferred_name = self.user.first_name
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
