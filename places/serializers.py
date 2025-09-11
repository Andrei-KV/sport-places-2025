from rest_framework import serializers
from .models import Category, Place, Photo

class CategorySerializer(serializers.ModelSerializer):
    place_count = serializers.IntegerField(source='places.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'place_count']

class PlaceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'latitude', 'longitude']

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['image']

class PlaceDetailSerializer(serializers.ModelSerializer):
    first_photo = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ['id', 'name', 'description', 'latitude', 'longitude', 'first_photo']

    def get_first_photo(self, obj):
        first_photo = obj.first_photo
        if first_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_photo.image.url)
        return None
