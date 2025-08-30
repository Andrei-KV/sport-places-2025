from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from .models import Place, PendingPlace, Comment, Rating, Photo
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import PlaceForm, CommentForm, RatingForm
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
        form = PlaceForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a pending submission
            # by adding commit=False, we tell Django to create the object but not save it to the database yet
            pending_submission = form.save(commit=False)
            pending_submission.user = request.user
            pending_submission.action = 'add'
            pending_submission.save()

            # Сохраняем загруженные фото
            for f in request.FILES.getlist('photos'):
                Photo.objects.create(pending_place=pending_submission, image=f)

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
        form = PlaceForm(request.POST, request.FILES)
        if form.is_valid():
            pending_submission = form.save(commit=False)
            pending_submission.user = request.user
            pending_submission.action = 'edit'
            pending_submission.original_place = place
            pending_submission.save()

            # Сохраняем загруженные фото для заявки на редактирование
            for f in request.FILES.getlist('photos'):
                Photo.objects.create(pending_place=pending_submission, image=f)
# Будем сохранять фотографии, связанные с заявками на модерацию (PendingPlace), 
# а не с одобренными площадками (Place). 
# Это правильно, так как администратор должен видеть фотографии, которые он одобряет.                
            return redirect('home')
    else:
        form = PlaceForm(initial={'name': place.name, 'description': place.description})

    context = {'form': form, 'place': place}
    return render(request, 'places/edit_place.html', context)



@login_required # Добавим этот декоратор, чтобы оставлять комментарии могли только авторизованные пользователи
def place_detail(request, place_id):
    place = get_object_or_404(Place, pk=place_id)
    comments = place.comments.all().order_by('-created_at') # Получаем все комментарии для площадки

    # Получаем среднюю оценку
    average_rating = place.ratings.aggregate(models.Avg('value'))['value__avg']

    # Обработка форм
    if request.method == 'POST':
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.place = place
                new_comment.user = request.user
                new_comment.save()
                return redirect('place_detail', place_id=place.id)

        elif 'rating_submit' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                new_rating = rating_form.save(commit=False)
                new_rating.place = place
                new_rating.user = request.user
                new_rating.save()
                return redirect('place_detail', place_id=place.id)
    else:
        comment_form = CommentForm()
        rating_form = RatingForm()

    context = {
        'place': place,
        'comments': comments,
        'average_rating': average_rating,
        'comment_form': comment_form,
        'rating_form': rating_form
    }
    return render(request, 'places/place_detail.html', context)