from django import forms
from whiteboard.models import Note
import datetime

class NewNoteForm(forms.ModelForm):
	class Meta:
		model = Note
		fields = ['text']

	text = forms.CharField(widget=forms.Textarea)

	# def save(self, commit=True):
	# 	note = super(NewNoteForm, self).save(commit=False)
	# 	note.text = self.cleaned_data['email']
	# 	note.pub_date = datetime.datetime.today().date()
	# 	note.submitted_by = 

	# 	if commit:
	# 		note.save()
	# 	return note


