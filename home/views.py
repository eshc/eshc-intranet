from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime


from leases.models import Lease, Inventory

def index(request):
	# Check if info is updated
	user = request.user
	if user.is_authenticated():
		if user.first_name == '' or user.last_name == '' or user.profile.phone_number == '' or user.profile.perm_address == '':
			messages.add_message(request, messages.WARNING, 'Your Profile is missing information. Go fill in extra info!')
	return render(request, 'home/index.html')

def mail_test(request):
	if request.method != 'POST':
		pass
	else:
		send_mail(
		    'Subject here',
		    'Here is the message.',
		    'ESHC',
		    ['filip.kaklin@gmail.com'],
		    fail_silently=False,
		)
		return HttpResponseRedirect(reverse('home:index'))

	return render(request, 'home/mail_test.html')

@login_required
def profile(request):
	leases = Lease.objects.filter(user_id=request.user.id)
	valid_lease = False
	now = timezone.localdate()
	for lease in leases:
		if lease.start_date <= now <= lease.end_date:
			valid_lease = True
			break

	if valid_lease == False:
		messages.add_message(request, messages.WARNING, 'You do not have a valid lease registered! Have you signed one?')

	if not leases:
		messages.add_message(request, messages.INFO, 'You do not have any leases registered. They will appear here when you do.')

	context = {'leases': leases, 
		'share_received': request.user.profile.share_received, 
		'valid_lease': valid_lease,
		}

	return render(request, 'account/account/profile.html', context)

