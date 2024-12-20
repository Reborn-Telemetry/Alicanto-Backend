from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
  path("login", views.login_page, name="login"),
  path("no-access", views.no_access, name="no-access"),
  path("", views.dashboard, name="dashboard"),
  path("logout_user/", views.logout_user, name="logout_user"),
  path("bus_list/", views.bus_list, name="bus_list"),
  path("bus_list_view/", views.bus_list_view, name="bus_list_view"),
  path("dic_fusi/", views.dic_fusi, name="dic_fusi"),
  path("bus_detail/<str:pk>/", views.bus_detail, name="bus_detail"),
  path("create_bus/", views.create_bus, name="create_bus"),
  path("create_fusi/", views.create_fusi, name="create_fusi"),
  path("update_bus/<str:pk>/", views.update_bus, name="update_bus"),
  path('update-fusi-code/<str:pk>/', views.update_fusicode, name='update-fusi-code'),
  path("update_fusi/<str:pk>/", views.update_fusi, name="update_fusi"),
  path("delete_bus/<str:pk>/", views.delete_bus, name="delete_bus"),
  path("reports_page/", views.reports_page, name="reports_page"),
  path('energy_record/', views.energy_record, name='energy-record'),
  path("warnings/", views.warnings, name="warnings"),
  path("fusi_dashboard/", views.fusi_dashboard, name="fusi_dashboard"),
 

]

