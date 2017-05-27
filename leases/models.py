from django.db import models
from django.contrib.auth.models import User

class Lease(models.Model):
	user = models.ForeignKey(User)
	lease_type = models.CharField(max_length=10)
	start_date = models.DateField('start date')
	end_date = models.DateField('end date')
	building = models.PositiveIntegerField('building number')
	flat = models.PositiveIntegerField('flat number')
	room = models.CharField(max_length=1)
	date_signed = models.DateField('date signed')
