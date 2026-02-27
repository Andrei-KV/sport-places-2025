from rest_framework import serializers
from .models import Category, Place, Photo

class CategorySerializer(serializers.ModelSerializer):
    place_count = serializers.IntegerField(source='places.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'place_count']


class PlaceListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка площадок.
    Возвращает основную информацию, адрес и первое фото.
    """
    first_photo = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'first_photo']

    def get_first_photo(self, obj):
        """
        Возвращает URL первого фото площадки.
        """
        first_photo_obj = obj.first_photo
        if first_photo_obj and hasattr(first_photo_obj, 'image'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_photo_obj.image.url)
            return first_photo_obj.image.url
        return None


class PhotoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для фотографий.
    """
    class Meta:
        model = Photo
        fields = ['image']


class PlaceDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о площадке.
    Возвращает полную информацию и до 4 фотографий.
    """
    photos = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ['id', 'name', 'address', 'description', 'latitude', 'longitude', 'photos']

    def get_photos(self, obj):
        """
        Собирает до 4 URL-адресов фотографий для площадки.
        """
        # Получаем первые 4 фото
        photos = obj.photos.all()[:4]
        request = self.context.get('request')

        # Если есть request, строим абсолютные URL
        if request:
            return [request.build_absolute_uri(photo.image.url) for photo in photos]

        # В противном случае возвращаем относительные пути
        return [photo.image.url for photo in photos]
