from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
  path("", views.login_page, name="login"),
  path("bus_list/", views.bus_list, name="bus_list"),
  path("dic_fusi/", views.dic_fusi, name="dic_fusi"),
  path("odometer/", views.odometer, name="odometer"),
  path("bus_detail/<str:pk>/", views.bus_detail, name="bus_detail"),
  path("create_bus/", views.create_bus, name="create_bus"),
  path("create_fusi/", views.create_fusi, name="create_fusi"),
  path("update_bus/<str:pk>/", views.update_bus, name="update_bus"),
  path("update_fusi/<str:pk>/", views.update_fusi, name="update_fusi"),
  path("delete_bus/<str:pk>/", views.delete_bus, name="delete_bus")
    
]

