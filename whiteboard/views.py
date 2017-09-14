from django.shortcuts import render
from whiteboard.models import Note
import datetime

from django.contrib.auth.decorators import login_required

from users.decorators import has_share

# Create your views here.

@login_required
@has_share
def index(request):
	notes = Note.objects.all()
	context = {'notes': notes}
	today = datetime.datetime.today().date()

	current_notes = [note if note.pub_date+datetime.timedelta(days=7) >= today else note.delete() for note in notes]

	context = {'notes': current_notes}
	return render(request, 'whiteboard/whiteboard.html', context)

