from django import forms
from .models import Place, PendingPlace, Comment, Rating, Category

class PlaceForm(forms.ModelForm):
    # Поле для выбора существующей категории
    existing_category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('name'),
        required=False,
        empty_label="Выберите категорию"
    )
    # Поле для ввода новой категории, если ее нет в списке
    new_category_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = PendingPlace
        fields = ['name', 'description', 'latitude', 'longitude']


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
