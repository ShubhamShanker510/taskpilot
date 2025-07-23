from django import forms

from ..models import *


# create task form
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "project",
            "title",
            "description",
            "assigned_to",
            "status",
            "due_date",
        ]
        widgets = {
            "project": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "assigned_to": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "due_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
