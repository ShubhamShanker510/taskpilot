from django import forms
from .models import *

# create project form
class createProject(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'deadline']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }