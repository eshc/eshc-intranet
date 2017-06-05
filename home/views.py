from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseRedirect

def index(request):
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
