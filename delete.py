import os
import django

# Указываем settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from places.models import Photo, PendingPlace
from django.core.files import File

# Берём первый PendingPlace
some_pending_place_instance = PendingPlace.objects.first()

# Загружаем файл
with open("test.png", "rb") as f:
    photo = Photo.objects.create(image=File(f), pending_place=some_pending_place_instance)

print("Загружено фото:", photo.image.url)
