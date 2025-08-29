from django.shortcuts import render, redirect, get_object_or_404
from .models import Place, PendingPlace
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import PlaceForm
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
            # После регистрации перенаправляет на страницу входа
            return redirect('login')  # Перенаправляем на страницу входа
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


@login_required
def add_place(request):
    if request.method == 'POST':
        form = PlaceForm(request.POST)
        if form.is_valid():
            # Create a pending submission
            # by adding commit=False, we tell Django to create the object but not save it to the database yet
            pending_submission = form.save(commit=False)
            pending_submission.user = request.user
            pending_submission.action = 'add'
            pending_submission.save()

# pending_submission.save(): Now that we've made all the necessary changes to the object in memory, 
# we call .save() without any parameters. This finalizes the process 
# and saves the pending_submission object to the PendingPlace table in the database

            return redirect('home')  # Redirect to home after submission
    else:
        form = PlaceForm()

    context = {'form': form}
    return render(request, 'places/add_place.html', context)

@login_required
def edit_place(request, place_id):
    place = get_object_or_404(Place, pk=place_id)

    if request.method == 'POST':
        form = PlaceForm(request.POST)
        if form.is_valid():
            pending_submission = form.save(commit=False)
            pending_submission.user = request.user
            pending_submission.action = 'edit'
            pending_submission.original_place = place
            pending_submission.save()
            return redirect('home')
    else:
        form = PlaceForm(initial={'name': place.name, 'description': place.description})

    context = {'form': form, 'place': place}
    return render(request, 'places/edit_place.html', context)

