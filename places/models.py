from django.db import models
from django.contrib.auth.models import User

# Модель для одобренных площадок
class Place(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

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

    # Связи и статус модерации
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_place = models.ForeignKey(Place, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    def __str__(self):
        return f"{self.action.capitalize()} - {self.name}"
