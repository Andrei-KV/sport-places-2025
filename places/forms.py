from django import forms
from .models import Place, PendingPlace, Comment, Rating

class PlaceForm(forms.ModelForm):
    
    latitude = forms.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, required=False)

    class Meta:
        model = PendingPlace
        fields = ['name', 'description']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
