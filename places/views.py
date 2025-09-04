from django.db import models
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Place, PendingPlace, Comment, Rating, Photo, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import PlaceForm, CommentForm, RatingForm
import folium


def home_page(request):
    # Получаем 8 самых популярных категорий
    popular_categories = Category.objects.order_by('-view_count')[:8]
    # Получаем остальные категории в алфавитном порядке
    other_categories = Category.objects.exclude(
        pk__in=popular_categories.values('pk')
    ).order_by('name')

    # Получаем 8 самых популярных площадок по среднему рейтингу
    #    (Аннотируем каждую площадку средним рейтингом и сортируем по убыванию)
    popular_places = Place.objects.annotate(
        average_rating=models.Avg('ratings__value')
    ).filter(
        # Не показывать площадки без рейтинга, если это нужно
        average_rating__isnull=False
    ).order_by(models.F('average_rating').desc(nulls_last=True))[:8]

    # Контекст, чтобы передавать популярные площадки
    context = {
        'popular_categories': popular_categories,
        'other_categories': other_categories,
        'popular_places': popular_places,
    }
    return render(request, 'places/home.html', context)

def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    # Увеличиваем счетчик просмотров при каждом посещении
    category.view_count += 1
    category.save()

    # Получаем все площадки, относящиеся к этой категории
    # и сразу аннотируем их средним рейтингом
    places = category.places.all().annotate(average_rating=models.Avg('ratings__value'))

    # Создаем карту с маркерами для всех площадок
    place_map = None
    if places:
        # Центрируем карту по первой площадке
        center_lat = places.first().latitude
        center_lon = places.first().longitude
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

        for place in places:
            yandex_maps_url = f"https://yandex.ru/maps/?rtext=~{place.latitude},{place.longitude}&z=15"
            first_photo = place.first_photo
            place_detail_url = request.build_absolute_uri(reverse('place_detail', args=[place.id]))
            # Проверяем, существует ли фотография
            if first_photo:
                # Получаем абсолютный URL для фото, используя request
                photo_url = request.build_absolute_uri(first_photo.image.url)
                

                # HTML-содержимое для iframe с абсолютным URL
                iframe_html = f"""
                    <style>
                        body, html {{
                            margin: 0 !important;
                            padding: 0 !important;
                        }}
                    </style>
                    <div style="
                        display: flex; 
                        flex-direction: column; 
                        width: 100%; 
                        height: 100%; 
                        box-sizing: border-box; 
                        font-family: Arial, sans-serif;
                    ">
                        <div style="
                            position: relative; 
                            width: 100%; 
                            height: 100%; 
                            overflow: hidden; 
                            border-radius: 4px;
                        ">
                            <img src="{photo_url}"
                                style="
                                    position: absolute; 
                                    top: 0; 
                                    left: 0; 
                                    width: 100%; 
                                    height: 100%; 
                                    object-fit: cover;
                                "
                                alt="{place.name} фото">
                        </div>
                        
                        <div style="padding: 10px 10px 0 10px; flex-grow: 1;">
                            <h3 style="
                                margin-top: 0; 
                                margin-bottom: 5px; 
                                font-size: 1em;
                            ">
                                <a href="{place_detail_url}" 
                                    target="_top"
     onclick="L.DomEvent.stopPropagation(event);"
                                    style="color: #007bff; text-decoration: none; font-weight: bold;"
                                >{place.name}</a>
                            </h3>
                            <a href="{yandex_maps_url}" 
                                target="_blank"
                                onclick="return L.DomEvent.stopPropagation(event);" 
                                style="color: #555; font-size: 0.9em; text-decoration: none;"
                                >Построить маршрут</a>
                        </div>
                    </div>
                """
            else:
                # Если фото нет, отображаем только название и ссылку
                iframe_html = f"""
                <h3 style="margin-bottom: 5px; font-size: 1em;"><a href="{place_detail_url}" target="_parent" style="color: #007bff; text-decoration: none; font-weight: bold;">{place.name}</a></h3>
                <a href="{yandex_maps_url}" target="_blank" style="color: #555; font-size: 0.9em; text-decoration: none;">Построить маршрут</a>
                """
            
            # Создаём IFrame с фиксированной шириной и адаптивной высотой
            iframe = folium.IFrame(html=iframe_html, width="200px", height="auto",)
            
            # Popup с максимальной шириной 200px
            popup = folium.Popup(iframe, max_width="200px", max_height="400px")

            folium.Marker(
                [place.latitude, place.longitude],
                tooltip=place.name,
                popup=popup
            ).add_to(m)

        place_map = m._repr_html_()
    
    # Добавляем все категории в контекст для выпадающего списка
    all_categories = Category.objects.all()
    context = {
        'current_category': category,
        'places': places,
        'place_map': place_map,
        'all_categories': all_categories,
    }
    return render(request, 'places/category_detail.html', context)

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
            # Обработка категории
            existing_category = form.cleaned_data.get('existing_category')
            new_category_name = form.cleaned_data.get('new_category_name')
            category = None

            if new_category_name:
                # Если введена новая категория, создаем ее
                category, created = Category.objects.get_or_create(name=new_category_name)
            elif existing_category:
                # Иначе используем выбранную
                category = existing_category

            pending_place = form.save(commit=False)
            pending_place.user = request.user
            pending_place.action = 'add'
            pending_place.category = category # Сохраняем категорию
            pending_place.save()

            for photo_file in request.FILES.getlist('photos'):
                Photo.objects.create(image=photo_file, pending_place=pending_place)

            return redirect('home')
    else:
        form = PlaceForm()
    
    context = {'form': form, 'categories': Category.objects.all().order_by('name')}
    return render(request, 'places/add_place.html', context)

# pending_submission.save(): Now that we've made all the necessary changes to the object in memory, 
# we call .save() without any parameters. This finalizes the process 
# and saves the pending_submission object to the PendingPlace table in the database


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
            
            # Чтобы сохранить оригинальное название
            # Так как не передаётся пользователем
            # Теперь, даже если поле name не будет отправлено с формы, 
            # мы берем его из объекта place и сохраняем в заявке 
            # pending_submission, гарантируя, что оно не потеряется.
            pending_submission.name = place.name
            pending_submission.save()
            # Сохранение координат
            pending_submission.latitude = form.cleaned_data['latitude']
            pending_submission.longitude = form.cleaned_data['longitude']
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
@login_required 
def place_detail(request, place_id):
    place = get_object_or_404(Place, pk=place_id)
    comments = place.comments.all().order_by('-created_at')
    photos = place.photos.all() # Получаем все фото для этой площадки

    # Получаем среднюю оценку
    average_rating = place.ratings.aggregate(models.Avg('value'))['value__avg']

    # Создаем карту
    place_map = None # Инициализируем переменную
    if place.latitude and place.longitude:
        m = folium.Map(location=[place.latitude, place.longitude], zoom_start=12)
        folium.Marker(
            [place.latitude, place.longitude],
            tooltip=place.name
        ).add_to(m)
        place_map = m._repr_html_()

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
                value = rating_form.cleaned_data['value']
                user = request.user
                
                # Ищем существующую оценку или создаем новую
                rating, created = Rating.objects.get_or_create(
                    place=place,
                    user=user,
                    defaults={'value': value} # Значение для новой записи
                )
                
                # Если запись уже существовала, обновляем её значение
                if not created:
                    rating.value = value
                    rating.save()
                    
                return redirect('place_detail', place_id=place.id)
    else:
        comment_form = CommentForm()
        rating_form = RatingForm()

    context = {
        'place': place,
        'comments': comments,
        'average_rating': average_rating,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'photos': photos, 
        'place_map': place_map, 
    }
    return render(request, 'places/place_detail.html', context)
