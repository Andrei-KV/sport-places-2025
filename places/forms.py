from django import forms
from .models import Place, PendingPlace

class PlaceForm(forms.ModelForm):
    class Meta:
        model = PendingPlace
        fields = ['name', 'description']