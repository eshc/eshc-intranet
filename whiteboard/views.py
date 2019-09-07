from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect

from whiteboard.models import Note

import datetime

from django.contrib.auth.decorators import login_required

from users.decorators import current_member_required

from whiteboard.forms import NewNoteForm

# Create your views here.

@login_required
@current_member_required
def index(request):
	notes = Note.objects.all()
	context = {'notes': notes}
	today = datetime.datetime.today().date()

	# delete notes older than 7 days
	current_notes = [note if note.pub_date+datetime.timedelta(days=7) >= today else note.delete() for note in notes]

	context = {'notes': current_notes}
	return render(request, 'whiteboard/whiteboard.html', context)

def add_note(request):
	note_form = NewNoteForm()

	if request.method != 'POST':
		note_form = NewNoteForm()
	else:
		note_form = NewNoteForm(data=request.POST)

		if note_form.is_valid():
			text = note_form.cleaned_data['text']
			pub_date = datetime.datetime.today().date()
			submitted_by = request.user
			update = Note.objects.create(text=text, pub_date=pub_date, submitted_by=submitted_by)

			messages.add_message(request, messages.SUCCESS, 'Announcement added!')
			return HttpResponseRedirect(reverse('whiteboard:index'))
		else:
			messages.add_message(request, messages.WARNING, 'Something went wrong?')

	context = {'form': note_form}
	return render(request, 'whiteboard/add_note.html', context)


