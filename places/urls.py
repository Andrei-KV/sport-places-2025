from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('add/', views.add_place, name='add_place'),
    path('edit/<int:place_id>/', views.edit_place, name='edit_place'),
    path('register/', views.register, name='register'), 
]