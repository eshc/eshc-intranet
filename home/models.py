from django.db import models
from django.contrib.auth.models import User, Group

class GM(models.Model):
	def __str__(self):
		return 'GM'+str(self.number)

	number = models.IntegerField()
	date_conv = models.DateField('date convened')
	# minutes = models.FileField(upload_to='minutes/', default=None, null=True, blank=True)

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

	
