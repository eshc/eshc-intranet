from django.db import models
from django.contrib.auth.models import User

class Lease(models.Model):
	user = models.ForeignKey(User)
	lease_type = models.CharField(max_length=10)
	start_date = models.DateField('start date')
	end_date = models.DateField('end date')
