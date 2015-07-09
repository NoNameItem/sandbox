from django import forms
from django.contrib.auth.models import User
from django_project.models import UserProfile

__author__ = 'nonameitem'

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('sex', 'about')


class ImageUploadForm(forms.Form):
    image = forms.ImageField()

