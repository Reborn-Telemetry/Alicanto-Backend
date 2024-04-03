from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('dashboard_disponibilidad_flota/', views.dashboard_disponibilidad_flota, name='disponibilidad-flota'),
    path('matriz-km-diario-flota/', views.matriz_km_diario_flota, name='matriz-km-diario-flota-xmls'),
    path('disponibilidad_flota/', views.disponbilidad_flota, name='action-disponibilidad'),
]