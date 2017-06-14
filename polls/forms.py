from django import forms
from .models import Question
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import ugettext_lazy as _

import datetime
from django.utils import timezone


class QuestionSubmitForm(forms.ModelForm):

	class Meta:
		model = Question
		fields = ['question_title', 'question_text', 'close_date']#, 'submitted_by']
		labels = {
			'question_title': 'Proposal Title', 
			'question_text': 'Proposal Description', 
			'close_date': 'Close voting on:',
		}
		widgets = {
			'close_date': forms.SelectDateWidget(),
		}

	def clean_close_date(self):
		date = self.cleaned_data['close_date']
		if date < datetime.date.today():
			raise forms.ValidationError("The date cannot be in the past!")
		return date

	def save(self, commit=True):
		question = super(QuestionSubmitForm, self).save(commit=False)

		question.question_title = self.cleaned_data['question_title']
		question.question_text = self.cleaned_data['question_text']
		question.close_date = self.clean_close_date()

		if commit:
			question.save()
		return question

