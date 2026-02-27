from django import forms
from .models import Place, PendingPlace, Comment, Rating, Category
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


# your_app/forms.py
from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Переопределяем подписи полей на русский
        self.fields['username'].label = 'Имя пользователя или email'
        self.fields['password1'].label = 'Пароль'  # Изменено с 'password' на 'password1'
        self.fields['password2'].label = 'Подтверждение пароля'

        # Добавляем CSS-классы для стилизации
        self.fields['username'].widget.attrs.update({'class': 'form-group'})
        self.fields['password1'].widget.attrs.update({'class': 'form-group'})  # Изменено
        self.fields['password2'].widget.attrs.update({'class': 'form-group'})

    # Этот блок кода отвечает за переименование меток и не вызывает ошибку, 
    # но лучше использовать labels в классе Meta
    class Meta(UserCreationForm.Meta):
        labels = {
            'username': 'Имя пользователя или email',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        
    def clean_password2(self):
        # Здесь мы можем изменить подсказку для совпадения паролей
        password = self.cleaned_data.get('password2')
        password2 = self.cleaned_data.get('password1')
        if password and password2 and password != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя или email'
        self.fields['password'].label = 'Пароль'


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
        fields = ['name', 'address', 'description', 'latitude', 'longitude']


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