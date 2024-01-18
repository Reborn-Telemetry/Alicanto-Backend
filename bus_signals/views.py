from django.shortcuts import render


# Create your views here.

def login(request):
    return render(request, 'login.html')


def bus_list(request):
    return render(request, 'bus_signals/bus_list.html')


def dic_fusi(request):
    return render(request, 'bus_signals/dic_fusi.html')


def odometer(request):
    return render(request, 'bus_signals/odometer.html')
