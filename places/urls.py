from django.urls import path
from .views import (
    HomePageView,
    PlaceDetailView,
    PlaceCreateView,
    PlaceEditView,
    RegisterView,
    CategoryDetailView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('place/<int:place_id>/', PlaceDetailView.as_view(), name='place_detail'),
    path('add/', PlaceCreateView.as_view(), name='add_place'),
    path('edit/<int:place_id>/', PlaceEditView.as_view(), name='edit_place'),
    path('register/', RegisterView.as_view(), name='register'),
    path('category/<slug:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
]