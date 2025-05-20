from django import forms
from django.contrib.auth.models import User

class UsernameUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']