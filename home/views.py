from django.shortcuts import render
# from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.shortcuts import get_object_or_404
import datetime
import os
import csv

from leases.models import Lease, Inventory
from .forms import UserEditForm, ProfileEditForm, WgEditForm, PointAddForm, UpdateForm, MinutesForm

from users.decorators import has_share, check_grouup
from home.models import GM, Point, WgUpdate, Minutes
from whiteboard.models import Note

import sendgrid
from sendgrid.helpers.mail import *

import boto3
import botocore
import eshcIntranet.settings as settings

@login_required
def index(request):
	check_info_share(request)

	test = 'Lorem'

	# Create an S3 client
	s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
	    		aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
	    		config=botocore.client.Config(
	    			signature_version='s3v4',
	    			region_name='eu-west-2',
	    			)
    		)

	image = s3.generate_presigned_url('get_object', Params={
						'Bucket': 'eshc-bucket',
						'Key': 'media/dr.png'},
						)

	pdf = s3.generate_presigned_url('get_object', Params={
						'Bucket': 'eshc-bucket',
						'Key': 'minutes/2017.07.07_-_PhoneCoop_-_Internet_-_160gbp.pdf'
						}
					)

	gm = GM.objects.latest('date_conv')

	notes = Note.objects.all()
	today = datetime.datetime.today().date()

	# delete notes older than 7 days
	current_notes = [note if note.pub_date+datetime.timedelta(days=7) >= today else note.delete() for note in notes]

	context = {'gm': gm,
		'test': test,
		'image': image,
		'pdf': pdf,
		'notes': notes,
		}

	return render(request, 'home/index.html', context)

def mail_test(request):
	if request.method != 'POST':
		pass
	else:
		sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
		from_email = Email("edinburghstudenthousingcoop@gmail.com")
		to_email = Email("filip.kaklin@gmail.com")
		subject = "Sending with SendGrid is Fun"
		content = Content("text/plain", "and easy to do anywhere, even with Python")
		mail = Mail(from_email, subject, to_email, content)
		response = sg.client.mail.send.post(request_body=mail.get())
		print(response.status_code)
		print(response.body)
		print(response.headers)
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
	leases_28_1 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=28, flat=1)
	leases_28_2 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=28, flat=2)
	leases_28_3 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=28, flat=3)
	leases_28_4 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=28, flat=4)
	leases_28_5 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=28, flat=5)
	leases_28_6 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=28, flat=6)
	leases_28_7 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=28, flat=7)

	leases_34_1 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=1)
	leases_34_2 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=2)
	leases_34_3 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=3)
	leases_34_4 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=4)
	leases_34_5 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=5)
	leases_34_6 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=6)
	leases_34_7 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=7)
	leases_34_8 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=8)
	leases_34_9 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=9)
	leases_34_10 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=10)
	leases_34_11 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=11)
	leases_34_12 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=12)
	leases_34_13 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=13)
	leases_34_14 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=14)
	leases_34_15 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=15)
	leases_34_16 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=16)
	leases_34_17 = Lease.objects.filter(start_date__lte=datetime.date.today()).filter(end_date__gte=datetime.date.today()).filter(building=34, flat=17)

	context = {'leases': leases,
		'leases_28_1': leases_28_1,
		'leases_28_2': leases_28_2,
		'leases_28_3': leases_28_3,
		'leases_28_4': leases_28_4,
		'leases_28_5': leases_28_5,
		'leases_28_6': leases_28_6,
		'leases_28_7': leases_28_7,
		'leases_34_1': leases_34_1,
		'leases_34_2': leases_34_2,
		'leases_34_3': leases_34_3,
		'leases_34_4': leases_34_4,
		'leases_34_5': leases_34_5,
		'leases_34_6': leases_34_6,
		'leases_34_7': leases_34_7,
		'leases_34_8': leases_34_8,
		'leases_34_9': leases_34_9,
		'leases_34_10': leases_34_10,
		'leases_34_11': leases_34_11,
		'leases_34_12': leases_34_12,
		'leases_34_13': leases_34_13,
		'leases_34_14': leases_34_14,
		'leases_34_15': leases_34_15,
		'leases_34_16': leases_34_16,
		'leases_34_17': leases_34_17,
	}
	return render(request, 'home/map.html', context)

@login_required
@has_share
def gms(request):
	gms = GM.objects.all().order_by('number').reverse()
	context = {'gms': gms}
	return render(request, 'home/gms.html', context)

@login_required
@has_share
def archive(request):

	# Create an S3 client
	s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
	    		aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
	    		config=botocore.client.Config(
	    			signature_version='s3v4',
	    			region_name='eu-west-2',
	    			)
    		)

	oldest_archive_keys = [
		'minutes/2013_11_14.pdf',
		'minutes/2014_01_08.pdf',
		'minutes/2014_03_07.pdf',
		'minutes/2014_04_03.pdf',
		'minutes/2014_04_24.pdf',
		'minutes/2014_04_27.pdf',
		'minutes/2014_05_01.pdf',
		'minutes/2014_05_15.pdf',
		'minutes/2014_05_22.pdf',
		'minutes/2014_06_06.pdf',
		'minutes/2014_06_10.pdf',
		'minutes/2014_06_19.pdf',
		'minutes/2014_06_26.pdf',
		'minutes/2014_07_03.pdf',
	]

	year_1_archive_keys = [
		'minutes/2014_09_17_1st GM Minutes.pdf',
		'minutes/2014_09_24_2nd GM Minutes.pdf',
		'minutes/2014_10_12_4th GM Minutes.pdf',
		'minutes/2014_10_19_5thGM.pdf',
		'minutes/2014_10_26_6thGM.pdf',
		'minutes/2014_11_05_7thGM.pdf',
		'minutes/2014_11_16_8thGM.pdf',
		'minutes/2014_11_26_9thGM.pdf',
		'minutes/2014_12_07_10thGM.pdf',
		'minutes/2015_01_11_11thGM.pdf',
		'minutes/2015_01_25_12thGM.pdf',
		'minutes/2015_02_08_13thGM.pdf',
		'minutes/2015_02_22_14thGM.pdf',
		'minutes/2015_03_08_15thGM.pdf',
		'minutes/2015_03_22_16thGM.pdf',
		'minutes/2015_03_30_SpecialGM.pdf',
		'minutes/2015_04_05_17thGM.pdf',
		'minutes/2015_04_19_18thGM.pdf',
		'minutes/2015_05_03_19thGM.pdf',
		'minutes/2015_05_17_20thGM.pdf',
		'minutes/2015_05_31_21stGM.pdf',
		'minutes/2015_06_14_22ndGM.pdf',
		'minutes/2015_06_28_23rdGM.pdf',
		'minutes/2015_07_12_24thGM.pdf',
		'minutes/2015_07_26_25thGM.pdf',
		'minutes/2015_08_09_26thGM.pdf',
		'minutes/2015_08_23_27thGM.pdf',
		'minutes/2015_09_06_28thGM.pdf',
	]

	further_archive_keys = [
		'minutes/29th_gm_2015_09_20.pdf',
		'minutes/30th_gm_2015_10_04.pdf',
		'minutes/31st_2015_10_18.pdf',
		'minutes/32ndGM_2015_11_01.pdf',
		'minutes/33rd_GM_15_11_2015.pdf',
		'minutes/34th General Meeting 29_11_2015.pdf',
		'minutes/35th General Meeting Minutes 2015.12.13.pdf',
		'minutes/36th General Meeting Minutes 2016.01.17.pdf',
		'minutes/37th General Meeting, 31_01_2016.pdf',
		'minutes/38thGeneralMeetingAgenda14022016_POSTPONED.pdf',
		'minutes/38th General Meeting Agenda _ re-convened 21.02.2016.pdf',
		'minutes/39th GM Minutes 28_02_2016.pdf',
		'minutes/40th General Meeting 2016.03.13.pdf',
		'minutes/41st General Meeting 2016.04.03.pdf',
		'minutes/42nd General Meeting (2nd AGM) 2016.10.04.pdf',
		'minutes/43rd General Meeting 2016.04.24.pdf',
		'minutes/44th General Meeting Agenda, 08_05_2016.pdf',
		'minutes/45th GM Meeting Agenda 22_05_2016.pdf',
		'minutes/46th General Meeting, 05_06_2016_.pdf',
		'minutes/47th Annual General Meeting Agenda, 03_07_2016.pdf',
		'minutes/48th General Meeting Agenda, 17_07_2016.pdf',
		'minutes/49th General Meeting Agenda, 31_07_2016.pdf',
		'minutes/50th General Meeting Agenda, 07_08_16.pdf',
		'minutes/51st General Meeting Agenda, 04_09_2016.pdf',
		'minutes/52nd General Meeting Agenda, 18_09_2016.pdf',
		'minutes/53rd General Meeting Agenda, 02_10_16.pdf',
		'minutes/54th General Meeting Agenda, 16_10_16.pdf',
		'minutes/55th General Meeting Agenda - 30_10_16.pdf',
		'minutes/56th General Meeting Agenda - 13_11_16.pdf',
		'minutes/57th General Meeting Agenda.pdf',
		'minutes/58th Meeting Agenda 2016_12_11.pdf',
		'minutes/59th General Meeting Agenda - 15_01_17.pdf',
		'minutes/60th General Meeting Agenda - 05_02_17 [the postponed meeting].pdf',
		'minutes/60th General Meeting Agenda - 29_01_17.pdf',
		'minutes/61st General Meeting Agenda - 12_02_17.pdf',
		'minutes/62nd_GM_26_02_2017.pdf',
		'minutes/63rd General Meeting Minutes [postponed] - 12_03_17.pdf',
		'minutes/64th General Meeting Agenda 09_04_17.pdf',
		'minutes/65th General Meeting Agenda 2017.04.23.pdf',
		'minutes/66th General Meeting Agenda 07_05_2017.pdf',
		'minutes/67th General Meeting Agenda 21_05_2017.pdf',
		'minutes/68th General Meeting Agenda 4_06_17.pdf',
		'minutes/69th General Meeting Agenda 02.07.17.pdf',
		'minutes/70th General Meeting Agenda 09_07_17.pdf',
		'minutes/71st General Meeting Agenda 23_07_17.pdf',
		'minutes/72nd General Meeting Agenda 06_08_17.pdf',
	]

	oldest_gms = [s3.generate_presigned_url('get_object', Params={'Bucket': 'eshc-bucket',	'Key': x}) for x in oldest_archive_keys]
	year_1_gms = [s3.generate_presigned_url('get_object', Params={'Bucket': 'eshc-bucket',	'Key': x}) for x in year_1_archive_keys]
	further_gms = [s3.generate_presigned_url('get_object', Params={'Bucket': 'eshc-bucket',	'Key': x}) for x in further_archive_keys]

	oldest_gms = zip(oldest_gms, [x[8:] for x in oldest_archive_keys])

	counter = [1,2]+list(range(4,17))+['S']+list(range(17,29))
	year_1_gms = zip(year_1_gms, [x[8:] for x in year_1_archive_keys], counter)

	counter2 = list(range(29,39))+[38]+list(range(39,61))+[60]+list(range(61,73))
	further_gms = zip(further_gms, [x[8:] for x in further_archive_keys], counter2)


	context = {'oldest_gms': oldest_gms,
		'year_1_gms': year_1_gms,
		'further_gms': further_gms,
		}
	return render(request, 'home/archive.html', context)


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

	s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    		aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    		config=botocore.client.Config(
    			signature_version='s3v4',
    			region_name='eu-west-2',
    			)
		)

	if Minutes.objects.filter(gm=gm).exists():
		file = s3.generate_presigned_url('get_object', Params={
					'Bucket': 'eshc-bucket',
					'Key': Minutes.objects.get(gm=gm).minutes_file.name},
					)
	else:
		file = '#'

	proposals = gm.point_set.filter(proposal=True)
	discussions = gm.point_set.filter(proposal=False)
	context = {'gm': gm, 'proposals': proposals, 'discussions': discussions,
		 'today': datetime.datetime.now(),
		 'places_updates': places_updates, 
		 'people_updates': people_updates, 
		 'participation_updates': participation_updates, 
		 'procedures_updates': procedures_updates,
		 'file': file,
		  }
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
			text = update_form.cleaned_data['text']
			group = update_form.cleaned_data['group']
			update = WgUpdate.objects.create(text=text, group=group, choice=gm)

			messages.add_message(request, messages.SUCCESS, 'WG Update added successfully!')
			return HttpResponseRedirect(reverse('home:agenda', args=(gm.id,)))
		else:
			messages.add_message(request, messages.WARNING, 'Something went wrong?')


	context = {'gm': gm, 'form': update_form}
	return render(request, 'home/submit_update.html', context)

@login_required
@has_share
@check_grouup('Procedures WG')
def upload_minutes(request, id):
	gm = get_object_or_404(GM, pk=id)

	if request.method != 'POST':
		minutes_form = MinutesForm()
	else:
		minutes_form = MinutesForm(request.POST, request.FILES)

		if minutes_form.is_valid():
			instance = Minutes.objects.create(minutes_file=request.FILES['minutes_file'], gm=gm)
			messages.add_message(request, messages.SUCCESS, 'Minutes uploaded successfully!')
			return HttpResponseRedirect(reverse('home:agenda', args=(gm.id,)))
		else:
			messages.add_message(request, messages.WARNING, 'Something went wrong?')


	context = {'gm': gm, 'form': minutes_form}
	return render(request, 'home/upload_minutes.html', context)

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

@login_required
@has_share
def groups(request):
	# groups = Group.objects.all()

	wgs = Group.objects.filter(name__endswith='WG')
	wgs_with_conv = [(wg, Group.objects.filter(name__endswith='Conv', name__startswith=wg.name)[0]) for wg in wgs]

	supers = User.objects.filter(is_superuser=True)
	staff = User.objects.filter(is_staff=True)

	context = {'wgs': wgs_with_conv,
		'supers': supers,
		'staff': staff,
		}
	return render(request, 'home/groups.html', context)

@login_required
@has_share
def cash(request):
	context = {}

	s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
	    		aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
	    		config=botocore.client.Config(
	    			signature_version='s3v4',
	    			region_name='eu-west-2',
	    			)
    		)

	s3.meta.client.download_file('eshc-bucket', 'money/year_1.csv', '/tmp/year_1.csv')
	with open('/tmp/year_1.csv', 'r') as csvfile:
		# context['y1_data'] = str(data.read(), "utf-8")
		reader = csv.reader(csvfile, delimiter = ',')
		rows = []
		total = 0
		for row in reader:
			total += float(row[3].replace(',',''))
			# rows.append([str(datetime.datetime.strptime(row[0], '%d/%m/%Y').date()), total])
			date = datetime.datetime.strptime(row[0], '%d/%m/%Y').date()
			rows.append({'year': date.year, 'month': date.month, 'day': date.day, 'total': total})
			# rows.append([date, total])

		context['y1_data'] = rows

	s3.meta.client.download_file('eshc-bucket', 'money/year_2.csv', '/tmp/year_2.csv')
	with open('/tmp/year_2.csv', 'r') as csvfile:
		# context['y1_data'] = str(data.read(), "utf-8")
		reader = csv.reader(csvfile, delimiter = ',')
		rows = []
		# total = 0
		for row in reader:
			total += float(row[3].replace(',',''))
			# rows.append([str(datetime.datetime.strptime(row[0], '%d/%m/%Y').date()), total])
			date = datetime.datetime.strptime(row[0], '%d/%m/%Y').date()
			rows.append({'year': date.year, 'month': date.month, 'day': date.day, 'total': total})
			# rows.append([date, total])

		context['y2_data'] = rows

	s3.meta.client.download_file('eshc-bucket', 'money/year_3.csv', '/tmp/year_3.csv')
	with open('/tmp/year_3.csv', 'r') as csvfile:
		# context['y1_data'] = str(data.read(), "utf-8")
		reader = csv.reader(csvfile, delimiter = ',')
		rows = []
		# total = 0
		for row in reader:
			total += float(row[3].replace(',',''))
			# rows.append([str(datetime.datetime.strptime(row[0], '%d/%m/%Y').date()), total])
			date = datetime.datetime.strptime(row[0], '%d/%m/%Y').date()
			rows.append({'year': date.year, 'month': date.month, 'day': date.day, 'total': total})
			# rows.append([date, total])

		context['y3_data'] = rows

	s3.meta.client.download_file('eshc-bucket', 'money/year_4.csv', '/tmp/year_4.csv')
	with open('/tmp/year_4.csv', 'r') as csvfile:
		# context['y1_data'] = str(data.read(), "utf-8")
		reader = csv.reader(csvfile, delimiter = ',')
		rows = []
		# total = 0
		for row in reader:
			total += float(row[3].replace(',',''))
			# rows.append([str(datetime.datetime.strptime(row[0], '%d/%m/%Y').date()), total])
			date = datetime.datetime.strptime(row[0], '%d/%m/%Y').date()
			rows.append({'year': date.year, 'month': date.month, 'day': date.day, 'total': total})
			# rows.append([date, total])

		context['y4_data'] = rows

	return render(request, 'home/cash_overview.html', context)


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
	# now = timezone.localdate()	# django 1.11
	now = timezone.now().date()		# django 1.10
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

