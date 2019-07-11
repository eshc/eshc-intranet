from django.db import models
from django.contrib.auth.models import User
from django.db.models import CASCADE


class Lease(models.Model):
	user = models.ForeignKey(User, on_delete=CASCADE)
	lease_type = models.CharField(max_length=10)
	start_date = models.DateField('start date')
	end_date = models.DateField('end date')
	building = models.PositiveIntegerField('building number')
	flat = models.PositiveIntegerField('flat number')
	room = models.CharField(max_length=1)
	date_signed = models.DateField('date signed')

class Inventory(models.Model):
	lease = models.OneToOneField(Lease, unique=True, on_delete=CASCADE)
	sub_date = models.DateField('submission date')
	inventory_notes = models.TextField(max_length=500)
