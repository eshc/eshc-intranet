from django import forms
from django.contrib.auth.models import User
from users.models import Profile
from django.contrib.auth.models import Group

from home.models import Point, WgUpdate

class UserEditForm(forms.ModelForm):
	"""
	A form that edits a user.
	"""
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']
		# fields = '__all__'

	def save(self, commit=True):
		user = super(UserEditForm, self).save(commit=False)
		# user.set_password(self.cleaned_data["password1"])
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.email = self.cleaned_data['email']

		if commit:
			user.save()
		return user

class ProfileEditForm(forms.ModelForm):
	"""
	A form to edit Profile data
	"""
	class Meta:
		model = Profile
		fields = ['phone_number', 'perm_address']

class WgEditForm(forms.Form):
	"""
	Form used in the profile view, to select WG membership.
	"""
	places = forms.BooleanField(required=False)
	people = forms.BooleanField(required=False)
	procedures = forms.BooleanField(required=False)
	participation = forms.BooleanField(required=False)

class PointAddForm(forms.ModelForm):
	"""
	Used to add discussion points and proposals to upcoming GMS
	"""
	class Meta:
		model = Point
		fields = ['title','description','proposal']
		labels = {
			'title': 'Title', 
			'description': 'Description', 
		}

class UpdateForm(forms.ModelForm):
	"""
	Used to add WG updates to upcoming GMs
	"""

	class Meta:
		model = WgUpdate
		fields = ['text', 'group']

