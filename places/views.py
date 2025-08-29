from django.shortcuts import render, redirect
from .models import Place
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

def home_page(request):
    all_places = Place.objects.all()  # Получаем все площадки из базы данных
    context = {
        'title': 'Каталог спортивных площадок',
        'places': all_places,  # Передаём список площадок в контекст
    }
    return render(request, 'places/home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Перенаправляем на страницу входа
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)