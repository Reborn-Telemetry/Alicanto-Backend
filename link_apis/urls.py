from django.urls import path, include
from rest_framework.routers import DefaultRouter
<<<<<<< HEAD
from . import views

router = DefaultRouter()
router.register(r'buses', views.BusViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ask_ai/', views.ask_ai, name='ask_ai' )
=======
from .views import BusViewSet

router = DefaultRouter()
router.register(r'buses', BusViewSet)

urlpatterns = [
    path('', include(router.urls)),
>>>>>>> 2a89e5d7a058ff36b143b661ec00d3f6807d3efa
]