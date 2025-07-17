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

    image=forms.ImageField(required=False)
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Write something about yourself...'
        })
    )
    
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirmPassword = forms.CharField(widget=forms.PasswordInput(), required=False)
    current_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'image', 'bio']

    def __init__(self, *args, **kwargs):
        # Get the user instance if passed
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        # If creating a new user (no instance), make username, email, and password required
        if self.instance is None or self.instance.pk is None:
            self.fields['username'].required = True
            self.fields['email'].required = True
            self.fields['password'].required = True
            self.fields['confirmPassword'].required = True
        else:
            # If editing, only username and email should be required
            self.fields['username'].required = True
            self.fields['email'].required = True

class LoginForm(forms.Form):
    username=forms.CharField(required=True)
    password=forms.CharField(required=True, widget=forms.PasswordInput)