from django import forms
from .models import *

class createProject(forms.ModelForm):
    
    class Meta:
        model=Project
        fields=['name', 'description']
    