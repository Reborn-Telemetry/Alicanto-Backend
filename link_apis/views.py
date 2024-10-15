from django.shortcuts import render
from bus_signals.models import Bus

# Create your views here.
from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = '__all__'

class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.bus.all()
    serializer_class = BusSerializer