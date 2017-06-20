from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

from leases.models import Lease, Inventory
from .forms import UserEditForm, ProfileEditForm

@login_required
def index(request):
	# Check if info is updated
	user = request.user
	if user.is_authenticated():
		if user.first_name == '' or user.last_name == '' or user.profile.phone_number == '' or user.profile.perm_address == '':
			messages.add_message(request, messages.WARNING, 'Your <a href="/accounts/profile/" class="alert-link">Profile</a> is missing information. Go fill in extra info!', extra_tags='safe')
		if request.user.profile.share_received == False:
			messages.add_message(request, messages.WARNING, 
				'We have not yet received your share. Have you bought one? ')

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

	if request.user.profile.share_received == False:
		messages.add_message(request, messages.WARNING, 'We have not yet received your share. Have you bought one?')

	context = {'leases': leases, 
		'share_received': request.user.profile.share_received, 
		'valid_lease': valid_lease,
		}

	return render(request, 'account/account/profile.html', context)

@login_required
def edit_profile(request):
	"""Edit user info"""
	user = request.user
	profile = user.profile

	if request.method != 'POST':
		# Display form filled with available info
		user_form = UserEditForm(initial={'first_name': user.first_name, 
			'last_name': user.last_name, 
			'email': user.email})
		profile_form = ProfileEditForm(initial={'phone_number': profile.phone_number, 
			'perm_address': profile.perm_address})
	else:
		user_form = UserEditForm(data=request.POST, instance=user)
		profile_form = ProfileEditForm(data=request.POST, instance=profile)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			return HttpResponseRedirect(reverse('profile'))

	context = {'user_form': user_form, 'profile_form': profile_form}
	return render(request, 'account/account/edit_profile.html', context)

def map(request):
	# current leases
	leases = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today())

	context = {'leases': leases}
	return render(request, 'home/map.html', context)

