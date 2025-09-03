from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('place/<int:place_id>/', views.place_detail, name='place_detail'),
    path('add/', views.add_place, name='add_place'),
    path('edit/<int:place_id>/', views.edit_place, name='edit_place'),
    path('register/', views.register, name='register'), 
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    
    path('', views.home_page, name='about'),
    path('', views.home_page, name='contacts'),
    path('', views.home_page, name='categories'),

]