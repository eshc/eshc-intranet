from datetime import date
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.core.validators import MaxValueValidator



class GM(models.Model):

    def __str__(self):
        return 'GM' + str(self.number)

    number = models.IntegerField()
    date_conv = models.DateField('date convened')
    # minutes = models.FileField(upload_to='minutes/', default=None, null=True, blank=True)

    def is_upcoming(self):
        return date.today() <= self.date_conv

    def discussions(self):
        return len(self.point_set.filter(proposal=False))

    def proposals(self):
        return len(self.point_set.filter(proposal=True))

    def updates(self):
        return len(self.wgupdate_set.values())


class Point(models.Model):
    def __str__(self):
        return self.title

    proposal = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    pub_date = models.DateField('date published')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(GM, on_delete=models.CASCADE)


class WgUpdate(models.Model):
    def __str__(self):
        return self.text

    text = models.CharField(max_length=500)
    group = models.ForeignKey(Group, limit_choices_to=models.Q(name__endswith='WG'),
                              on_delete=models.CASCADE)

    choice = models.ForeignKey(GM, on_delete=models.CASCADE)


class Minutes(models.Model):
    gm = models.OneToOneField(GM, on_delete=models.CASCADE)
    minutes_file = models.FileField(upload_to='minutes/', null=True)


class LdapGroup(models.Model):
    def __str__(self):
        return self.ldap_cn.partition(',')[0].rpartition('=')[2] # extract from cn=*NAME*,ou=junk

    ldap_cn = models.CharField(max_length=128)
    description = models.TextField(max_length=500)


class Role(models.Model):
    def __str__(self):
        return self.role_name

    role_name = models.CharField(max_length=50)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    subgroup = models.TextField(max_length=500, blank=True, null=True)
    description = models.TextField(max_length=500)
    assigned_to = models.ManyToManyField(User, blank=True)
    past_holders = models.ManyToManyField(User, verbose_name="Past holders", related_name="past_roles", blank=True)
    ldap_groups = models.ManyToManyField(LdapGroup, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)



class Flat(models.Model):
   def __str__(self):
       return "{}/{}".format(self.building,self.flatno)
   flatno = models.PositiveIntegerField()
   size = models.PositiveIntegerField()
   building = models.PositiveIntegerField()  # make enum

   # ensure flat exists in building using validation
class Room(models.Model):
    def __str__(self):
        return "{}{}".format(self.flat,chr(ord('@')+self.roomno))

    readonly_fields = ('flat', 'roomno')
    current_occupant = models.OneToOneField(User,null=True,on_delete=models.SET_NULL,unique=True)
    flat = models.ForeignKey(Flat,on_delete=models.CASCADE)
    roomno = models.IntegerField(choices=[(1,'A'),(2,'B'),(3,'C'),(4,'D'),(5,'E')]) # enum A to E

   # ensure room exists in flat using validation
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['roomno','flat'],
                name='no_duplicate_rooms_in_flat'
            )
        ]

        ordering = ('flat','roomno')
