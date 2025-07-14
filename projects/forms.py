from django import forms
from .models import *

class createProject(forms.ModelForm):
    
    class Meta:
        models=Project
        fields=['name', 'description']
    