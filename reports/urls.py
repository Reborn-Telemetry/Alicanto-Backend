from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('disponibilidad-flota/', views.disponbilidad_flota, name='disponibilidad-flota'),
    path('matriz-km-diario-flota/', views.matriz_km_diario_flota, name='matriz-km-diario-flota-xmls'),
]