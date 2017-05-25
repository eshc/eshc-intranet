from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	ref_number = models.CharField('Bank Reference Number', max_length=8, blank=True)
	phone_number = models.CharField(max_length=15, blank=True)
	perm_address = models.TextField(max_length=500, blank=True)

	# full_name = 'string'
	# full_name = models.
	# full_name = User.objects.get(username=user)
	# full_name = User.objects.get(user)

	# def full_name(self):
	# 	name = 	User.objects.get(id=user.id)
	# 	return name
		
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()
