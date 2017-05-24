from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .forms import UserEditForm, ProfileEditForm


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

@login_required
def edit_profile(request):
	"""Edit user info"""
	user = request.user
	profile = user.profile
	# a = User.objects.get(username=request.user.username)
	# a = user

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
			# user.first_name = form.cleaned_data['first_name']
			# user.last_name = form.cleaned_data['last_name']
			# user.email = form.cleaned_data['email']
			return HttpResponseRedirect(reverse('users:profile'))

	context = {'user_form': user_form, 'profile_form': profile_form}
	return render(request, 'users/edit_profile.html', context)
