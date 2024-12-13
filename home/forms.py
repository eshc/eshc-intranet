from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.models import User

from home.models import Point, WgUpdate, Minutes
from users.models import Profile

def validate_uoe_mail(value):
    if "ac.uk" in value:
        return False
    else:
        return True


class SignupWithProfileForm(SignupForm):
    first_name = forms.CharField(label="First name(s)", min_length=2, max_length=150,
                                 required=True, widget=forms.TextInput(
            attrs={"placeholder": "First name(s)", "autocomplete": "given-name"}
        ))
    last_name = forms.CharField(label="Last name(s)", min_length=2, max_length=150,
                                required=True, widget=forms.TextInput(
            attrs={"placeholder": "Last name(s)", "autocomplete": "family-name"}
        ))
    preferred_name = forms.CharField(label="Preferred name", max_length=40,
                                     required=False, widget=forms.TextInput(
            attrs={"placeholder": "Preferred name", "autocomplete": "nickname"}
        ))
    phone_number = forms.CharField(label="Phone number", max_length=15,
                                   required=False, widget=forms.TextInput(
            attrs={"placeholder": "Phone number", "autocomplete": "tel"}
        ))
    perm_address = forms.CharField(label="Permanent address", max_length=500,
                                        required=False, widget=forms.Textarea(
            attrs={"placeholder": "Permanent address", "autocomplete": "street-address"}
        ))
    captcha_question = forms.CharField(label="Security Question", max_length=80,
                                        required=True, widget=forms.TextInput(
                                            attrs={"placeholder": "What is the capital of Scotland?"}
                                            ))

    field_order = [
        "username",
        "first_name",
        "last_name",
        "preferred_name",
        "email",
        "email2",  # ignored when not present
        "password1",
        "password2",  # ignored when not present
        "phone_number",
        "perm_address",
        "captcha_question",
    ]

    def clean_email(self):
        if not validate_uoe_mail(self.cleaned_data['email']):
            self.add_error('email', 'Please do NOT use your university email address as this will lead to problems getting your deposit back when you leave the co-op.')
            return False
        return super(SignupWithProfileForm, self).clean_email()

    def signup(self, request, user: User):
        p, _ = Profile.objects.get_or_create(user=user)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        p.preferred_name = self.cleaned_data['preferred_name']
        p.phone_number = self.cleaned_data['phone_number']
        p.perm_address = self.cleaned_data['perm_address']
        p.full_clean()
        p.save()
        user.profile = p
        user.save()
        return user

    def save(self, request):
        if request.POST['captcha_question'].lower() != "edinburgh":
            raise forms.ValidationError('You should study some geography')
            return None
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(SignupWithProfileForm, self).save(request)

        # Add your own processing here.
        if self.signup(request, user):
            # You must return the original result.
            return user

class UserEditForm(forms.ModelForm):
    """
	A form that edits a user.
	"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    # fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

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
        fields = ['preferred_name', 'phone_number', 'perm_address']


class PointAddForm(forms.ModelForm):
    """
	Used to add discussion points and proposals to upcoming GMS
	"""

    class Meta:
        model = Point
        fields = ['title', 'description', 'proposal']
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


class MinutesForm(forms.ModelForm):
    """
	Used to add WG updates to upcoming GMs
	"""

    class Meta:
        model = Minutes
        fields = ['minutes_file']
