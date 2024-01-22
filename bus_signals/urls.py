from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
  path("", views.login, name="login"),
  path("bus_list/", views.bus_list, name="bus_list"),
  path("dic_fusi/", views.dic_fusi, name="dic_fusi"),
  path("odometer/", views.odometer, name="odometer"),
  path("bus_detail/<str:pk>/", views.bus_detail, name="bus_detail"),
    
]