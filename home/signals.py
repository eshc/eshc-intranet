#!/usr/bin/env python3
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from leases.models import Lease
from .models import Room
from datetime import date


@receiver(post_save,sender=Lease)
def update_map(sender,**kwargs):
    print(kwargs)
    lease = kwargs['instance']
    if (lease.end_date >= date.today()):
        Room.objects.filter(current_occupant=lease.user).update(current_occupant=None)
        Room.objects.filter(id=lease.room.id).update(current_occupant=lease.user)
