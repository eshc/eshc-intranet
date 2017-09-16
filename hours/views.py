from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from users.decorators import has_share

# Create your views here.

@login_required
@has_share
def index(request):
	
	context = {}
	return render(request, 'hours/logger.html', context)
