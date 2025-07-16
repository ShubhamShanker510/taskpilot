from django import forms
from .models import *
from users.models import *

class BulkNotificationForm(forms.Form):
    send_to = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        max_length=1000
    )