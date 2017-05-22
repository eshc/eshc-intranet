from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


def logout_view(request):
	"""Logout a user"""
	logout(request)
	return HttpResponseRedirect(reverse('home:index'))

def register(request):
	"""Register new user"""
	if request.method != 'POST':
		# Display blank registration form
		form = UserCreationForm()
	else:
		# Process completed form
		form = UserCreationForm(data=request.POST)

		if form.is_valid():
			new_user = form.save()
			# Log user in, redirect to home
			authenticated_user = authenticate(username=new_user.username, 
				password=request.POST['password1'])
			login(request, authenticated_user)
			return HttpResponseRedirect(reverse('home:index'))

	context = {'form': form}
	return render(request, 'users/register.html', context)

@login_required
def profile(request):
	return render(request, 'users/profile.html')
