from django.urls import path
from . import views

urlpatterns = [
    path('profiles', views.profile, name='profile'),
    path('work_order/', views.create_work_order, name='work_order_form'),
    path('update_ot/<str:pk>/', views.update_ot, name='update_ot'),

]