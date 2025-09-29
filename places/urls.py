from django.urls import path
from .views import (
    HomePageView,
    PlaceDetailView,
    PlaceCreateView,
    PlaceEditView,
    RegisterView,
    CategoryDetailView,
    TelegramAppView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('place/<int:place_id>/', PlaceDetailView.as_view(), name='place_detail'),
    path('add/', PlaceCreateView.as_view(), name='add_place'),
    path('edit/<int:place_id>/', PlaceEditView.as_view(), name='edit_place'),
    path('register/', RegisterView.as_view(), name='register'),
    path('category/<slug:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('telegram-app/', TelegramAppView.as_view(), name='telegram_app'),

    # Восстановленные URL-адреса, чтобы не нарушать работу основного сайта
    path('', HomePageView.as_view(), name='about'),
    path('', HomePageView.as_view(), name='contacts'),
    path('', HomePageView.as_view(), name='categories'),
]