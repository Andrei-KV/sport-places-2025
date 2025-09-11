from django.urls import path
from .api_views import (
    CategoryListAPIView,
    PlaceListAPIView,
    PlaceDetailAPIView,
)

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='api-category-list'),
    path('categories/<slug:category_slug>/places/', PlaceListAPIView.as_view(), name='api-place-list'),
    path('places/<int:pk>/', PlaceDetailAPIView.as_view(), name='api-place-detail'),
]
