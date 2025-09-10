from rest_framework import generics
from .models import Category, Place
from .serializers import CategorySerializer, PlaceListSerializer, PlaceDetailSerializer
from django.shortcuts import get_object_or_404

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all().prefetch_related('places')
    serializer_class = CategorySerializer

class PlaceListAPIView(generics.ListAPIView):
    serializer_class = PlaceListSerializer

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug)
        return Place.objects.filter(category=category)

class PlaceDetailAPIView(generics.RetrieveAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceDetailSerializer
    lookup_field = 'pk'
