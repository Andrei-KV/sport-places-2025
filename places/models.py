from django.db import models
from django.contrib.auth.models import User

# Модель для категорий площадок
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

# Модель для одобренных площадок
class Place(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='places')


    @property
    def first_photo(self):
        """Возвращает первое фото для использования в качестве миниатюры."""
        return self.photos.first()
    # @property — это декоратор в Python, который превращает метод класса в свойство. 
    # он позволяет вызывать метод, как будто это обычный атрибут (переменная), без скобок ()
    
    def __str__(self):
        return self.name
    

# Модель для заявок на модерацию
class PendingPlace(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]

    ACTION_CHOICES = [
        ('add', 'Добавление'),
        ('edit', 'Редактирование'),
        ('delete', 'Удаление'),
    ]

    # Данные о площадке
    name = models.CharField(max_length=200)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Связи и статус модерации
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_place = models.ForeignKey(Place, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.action.capitalize()} - {self.name}"


class Comment(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий от {self.user.username} на {self.place.name}'

class Rating(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        unique_together = ('place', 'user') # Один пользователь может оценить одну площадку только один раз

    def __str__(self):
        return f'Оценка {self.value} от {self.user.username} для {self.place.name}'


class Photo(models.Model):
    pending_place = models.ForeignKey(PendingPlace, on_delete=models.CASCADE, related_name='pending_photos', null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    image = models.ImageField(upload_to='place_photos/')

    def __str__(self):
        return f'Фото для {self.pending_place.name if self.pending_place else self.place.name}'
# place: A ForeignKey that links each photo to its corresponding Place object. 
# related_name='photos' will allow us to easily access all photos 
# for a place with place.photos.all().

# image: An ImageField is a special Django field that handles file uploads. 
# The upload_to='place_photos/' argument tells Django to save the images to 
# a sub-directory named place_photos inside your project's MEDIA_ROOT