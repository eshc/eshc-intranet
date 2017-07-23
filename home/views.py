from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.shortcuts import get_object_or_404
import datetime

from leases.models import Lease, Inventory
from .forms import UserEditForm, ProfileEditForm, WgEditForm, PointAddForm, UpdateForm

from users.decorators import has_share
from home.models import GM, Point, WgUpdate

@login_required
def index(request):
	check_info_share(request)
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
	leases, valid_lease = check_leases(request)
	check_info_share(request)

	groups = [x for x in Group.objects.values() if 'WG' in x['name']]

	places = Group.objects.get(name='Places WG')
	people = Group.objects.get(name='People WG')
	participation = Group.objects.get(name='Participation WG')
	procedures = Group.objects.get(name='Procedures WG')

	if request.method != 'POST':
		wg_form = WgEditForm(initial={'places': request.user in places.user_set.get_queryset(),
									'procedures': request.user in procedures.user_set.get_queryset(),
									'people': request.user in people.user_set.get_queryset(),
									'participation': request.user in participation.user_set.get_queryset(),})
	else:
		wg_form = WgEditForm(data=request.POST)
		# wg_form.places
		if wg_form.is_valid():
			messages.add_message(request, messages.SUCCESS, 'WG Membership updated successfully.')

			if wg_form.cleaned_data['places'] == True:
				places.user_set.add(request.user)
			else:
				places.user_set.remove(request.user)

			if wg_form.cleaned_data['people'] == True:
				people.user_set.add(request.user)
			else:
				people.user_set.remove(request.user)

			if wg_form.cleaned_data['procedures'] == True:
				procedures.user_set.add(request.user)
			else:
				procedures.user_set.remove(request.user)

			if wg_form.cleaned_data['participation'] == True:
				participation.user_set.add(request.user)
			else:
				participation.user_set.remove(request.user)

		return HttpResponseRedirect(reverse('profile'))

	context = {'leases': leases, 
		'share_received': request.user.profile.share_received, 
		'valid_lease': valid_lease,
		'groups': groups,
		'wg_form': wg_form
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

@login_required
@has_share
def map(request):
	# current leases
	leases = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today())

	context = {'leases': leases}
	return render(request, 'home/map.html', context)

@login_required
@has_share
def gms(request):
	gms = GM.objects.all().order_by('number').reverse()
	context = {'gms': gms}
	return render(request, 'home/gms.html', context)

@login_required
@has_share
def agenda(request, pk):
	gm = get_object_or_404(GM, pk=pk)
	places = Group.objects.get(name='Places WG')
	people = Group.objects.get(name='People WG')
	participation = Group.objects.get(name='Participation WG')
	procedures = Group.objects.get(name='Procedures WG')

	places_updates = WgUpdate.objects.filter(choice=gm, group=places)
	people_updates = WgUpdate.objects.filter(choice=gm, group=people)
	participation_updates = WgUpdate.objects.filter(choice=gm, group=participation)
	procedures_updates = WgUpdate.objects.filter(choice=gm, group=procedures)

	proposals = gm.point_set.filter(proposal=True)
	discussions = gm.point_set.filter(proposal=False)
	context = {'gm': gm, 'proposals': proposals, 'discussions': discussions,
		 'today': datetime.datetime.now(),
		 'places_updates': places_updates, 
		 'people_updates': people_updates, 
		 'participation_updates': participation_updates, 
		 'procedures_updates': procedures_updates, }
	return render(request, 'home/agenda.html', context)

@login_required
@has_share
def submit(request, id):
	gm = get_object_or_404(GM, pk=id)

	if request.method != 'POST':
		point_form = PointAddForm()
	else:
		point_form = PointAddForm(data=request.POST)

		if point_form.is_valid():
			messages.add_message(request, messages.SUCCESS, 'Agenda point added successfully!')
			title = point_form.cleaned_data['title']
			description = point_form.cleaned_data['description']
			proposal = point_form.cleaned_data['proposal']
			point = Point.objects.create(title=title, description=description, proposal=proposal, 
						pub_date=datetime.date.today(), submitted_by=request.user, choice=gm)

			return HttpResponseRedirect(reverse('home:agenda', args=(gm.id,)))

	context = {'gm': gm, 'form': point_form}
	return render(request, 'home/submit.html', context)
	
@login_required
@has_share
def submit_update(request, id):
	gm = get_object_or_404(GM, pk=id)

	if request.method != 'POST':
		update_form = UpdateForm()
	else:
		update_form = UpdateForm(data=request.POST)

		if update_form.is_valid():
			messages.add_message(request, messages.SUCCESS, 'WG Update added successfully!')
			text = update_form.cleaned_data['text']
			group = update_form.cleaned_data['group']
			update = WgUpdate.objects.create(text=text, group=group, choice=gm)

			return HttpResponseRedirect(reverse('home:agenda', args=(gm.id,)))

	context = {'gm': gm, 'form': update_form}
	return render(request, 'home/submit_update.html', context)

@login_required
@has_share
def delete(request, pk):
	point = get_object_or_404(Point, pk=pk)
	gm = get_object_or_404(GM, pk=point.choice.pk)
	context = {'point': point, 'gm': gm}

	if point.submitted_by.id != request.user.id:
		return HttpResponseRedirect(reverse('home:agenda', args=(gm.id,)))

	if request.method != 'POST':
		pass
	else:
		point.delete()
		return HttpResponseRedirect(reverse('home:agenda', args=(gm.id,)))

	return render(request, 'home/delete.html', context)


def check_info_share(request):
	# Check if info is updated and share received
	user = request.user
	if user.is_authenticated():
		if user.first_name == '' or user.last_name == '' or user.profile.phone_number == '' or user.profile.perm_address == '':
			messages.add_message(request, messages.WARNING, 'Your <a href="/accounts/profile/" class="alert-link">Profile</a> is missing information. Go fill in extra info!', extra_tags='safe')
		if request.user.profile.share_received == False:
			messages.add_message(request, messages.WARNING, 
				'We have not yet received your share. Have you bought one? ')
	return

def check_leases(request):
	leases = Lease.objects.filter(user_id=request.user.id)
	valid_lease = False
	inventories_made = False
	now = timezone.localdate()
	for lease in leases:
		if lease.start_date <= now <= lease.end_date:
			valid_lease = True
			break

	for lease in leases:
		if not Inventory.objects.filter(lease=lease).exists():
			messages.add_message(request, messages.WARNING, 'One of your leases is missing an inventory!')
			break 

	if valid_lease == False:
		messages.add_message(request, messages.WARNING, 'You do not have a valid lease registered! Have you signed one?')

	if not leases:
		messages.add_message(request, messages.INFO, 'You do not have any leases registered. They will appear here when you do.')

	return leases, valid_lease

