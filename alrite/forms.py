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
            'password',
            'healthy_facility',
            'is_nurse',
            'is_doctor',
        ]