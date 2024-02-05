from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('work_order/', views.create_work_order, name='work_order_form'),

]