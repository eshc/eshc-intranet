from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from users.decorators import current_member_required


# Create your views here.

@login_required
@current_member_required
def index(request):
    context = {}
    return render(request, 'hours/logger.html', context)
