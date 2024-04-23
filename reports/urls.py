from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('energy_report/', views.energy_report, name='energy-report'),
    path('dashboard_disponibilidad_flota/', views.dashboard_disponibilidad_flota, name='disponibilidad-flota'),
    path('matriz-km-diario-flota/', views.matriz_km_diario_flota, name='matriz-km-diario-flota-xmls'),
    path('disponibilidad_flota/', views.disponbilidad_flota, name='action-disponibilidad'),
    path('soh-flota/', views.reporte_soh_flota, name='reporte-soh-flota'),
    path("bus_dailykm_report_pdf/<str:pk>/", views.daily_bus_km_report_pdf, name="bus_dailykm_pdf_report"),
]