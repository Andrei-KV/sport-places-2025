from django import forms
from .models import Place, PendingPlace, Comment, Rating

class PlaceForm(forms.ModelForm):
    # Добавляем поле для множественной загрузки файлов
    photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

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
