from django import forms
from .models import *

from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError

class RegisterationForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    )

    # These fields are manually handled in view/template
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirmPassword = forms.CharField(widget=forms.PasswordInput(), required=False)
    current_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role']


class LoginForm(forms.Form):
    username=forms.CharField(required=True)
    password=forms.CharField(required=True, widget=forms.PasswordInput)