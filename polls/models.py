from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
	def __str__(self):
		return self.question_title

	question_title = models.CharField(max_length=200)
	question_text = models.TextField()
	pub_date = models.DateField('date published')
	close_date = models.DateField('close date')
	# closed = models.Boolean('closed')
	# closed = models.CharField('result')
	submitted_by = models.ForeignKey(User, on_delete=models.PROTECT)
	result = models.BooleanField(default=False)


class Choice(models.Model):
	def __str__(self):
		return self.choice_text

	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice_text = models.CharField(max_length=200)


class Vote(models.Model):

	choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	
