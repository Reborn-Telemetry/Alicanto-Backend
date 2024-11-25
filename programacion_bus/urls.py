from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('dashboard_programacion_buses/', views.programacion, name='programacion'),
    path('guardar_programacion/', views.guardar_programacion, name='guardar_programacion'),
   
    
]