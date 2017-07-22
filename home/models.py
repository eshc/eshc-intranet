from django.db import models
from django.contrib.auth.models import User

class GM(models.Model):
	def __str__(self):
		return 'GM'+str(self.number)

	number = models.IntegerField()
	date_conv = models.DateField('date convened')
	proposals = 1

	def discussions(self):
		return len(self.point_set.filter(proposal=False))

	def proposals(self):
		return len(self.point_set.filter(proposal=True))

class Point(models.Model):
	def __str__(self):
		return self.title

	proposal = models.BooleanField(default=False)
	title = models.CharField(max_length=200)
	description = models.TextField()
	pub_date = models.DateField('date published')
	submitted_by = models.ForeignKey(User, on_delete=models.PROTECT)
	choice = models.ForeignKey(GM, on_delete=models.PROTECT)
