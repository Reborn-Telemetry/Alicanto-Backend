from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('energy_report/', views.energy_report, name='energy-report'),
    path('dashboard_disponibilidad_flota/', views.dashboard_disponibilidad_flota, name='disponibilidad-flota'),
    path('matriz-km-diario-flota/', views.matriz_km_diario_flota, name='matriz-km-diario-flota-xmls'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('soh-flota/', views.reporte_soh_flota, name='reporte-soh-flota'),
    path("bus_dailykm_report_pdf/<str:pk>/", views.daily_bus_km_report_pdf, name="bus_dailykm_pdf_report"),
    path("historicos/", views.historical_data, name="historicos"),
    path("bus_historico/", views.historic_bus_report, name="bus_historico"),
    path("historico_energia/", views.historical_energy_report, name="historico_energia"),
    path("soh_historico/", views.historic_soh, name="soh_historico"),
    path("ultimo_voltaje_celdas/", views.last_value_cells_deltas, name="ultimo_voltaje_celdas"),
    path("ultimo_voltaje_celdas_excel/", views.last_value_cells_deltas_excel, name="ultimo_voltaje_celdas_excel"),
    path("rendimiento_bus/<int:pk>/", views.bus_performance_report_excel, name="bus_performance"),
    path("ecu_state/<int:pk>/", views.switch_report_xls, name="ecu_state"),
    path("drive_report/<int:pk>/", views.drive_report, name="drive_report"),
    path("pdf-report/", views.pdf_report, name="pdf-report"),
    path("software_version", views.software_version, name="software_version"),
    path("xls-report/", views.xls_report, name="xls-report"),
    path("monthly-bus-report-xls/", views.monthly_bus_report_xls, name="monthly-bus-report-xls"),
    path("recorrido_mensual_flota_pdf/", views.recorrido_mensual_flota, name="recorrido_mensual_flota_pdf"),
    path("recorrido_mensual_pdf/<str:pk>/", views.recorrido_mensual_bus_pdf, name="recorrido_mensual_pdf"),
    path("montly-km-report/", views.monthly_bus_report, name="montly-km-report"),
    path("recorrido-mensual-flota/", views.recorrido_mensual_flota_xls, name="recorrido-mensual-flota-xls"),
    path("bus_historic_fusi_pdf_report/<str:pk>/", views.bus_historic_fusi, name="bus_historic_fusi_pdf_report"),
    
]