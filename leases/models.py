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
	emergency_contact_name = models.CharField(verbose_name='emergency contact name', max_length=100, default='', blank=True)
	emergency_contact_phone = models.CharField(verbose_name='emergency contact phone', max_length=32, default='', blank=True)
	emergency_contact_address = models.TextField(verbose_name='emergency contact address', max_length=256, default='', blank=True)


class Covid(models.Model):
	user = models.ForeignKey(User, on_delete=CASCADE)
	building = models.PositiveIntegerField('building number')
	flat = models.PositiveIntegerField('flat number')
	room = models.CharField(max_length=1)
	covid_pos_date = models.DateField('Positive COVID-19 Test Date', null=True)


class Inventory(models.Model):
	lease = models.OneToOneField(Lease, unique=True, on_delete=CASCADE)
	sub_date = models.DateField('submission date')
	inventory_notes = models.TextField(max_length=500)
