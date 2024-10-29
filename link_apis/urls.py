from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'buses', views.BusViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ask_ai/', views.ask_ai, name='ask_ai' )
]