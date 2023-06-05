from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *


class CreateUser(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CreateUser, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['password'].required = True
        self.fields['healthy_facility'].required = True

    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'username',
            'password',
            'healthy_facility',
        ]

class CreateInviteForm(forms.Form):
    email = forms.EmailField(label="Email address")
    is_nurse = forms.BooleanField(label="Nurse status", required=False)
    is_doctor = forms.BooleanField(label="Doctor status", required=False)
    is_admin = forms.BooleanField(label="Admin status", required=False)

class AcceptInviteForm(forms.Form):
    first_name = forms.CharField(label="First name", max_length=150)
    last_name = forms.CharField(label="Last name", max_length=150)
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(label="Password", max_length=255, widget=forms.PasswordInput)
