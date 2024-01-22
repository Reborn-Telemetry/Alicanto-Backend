from django.shortcuts import render, redirect
from .models import Bus 
from .forms import BusForm


# Create your views here.

def login(request):
    return render(request, 'login.html')

def create_bus(request):
    form = BusForm()
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form}
    return render(request, 'bus_signals/bus_form.html', context)


def update_bus(request, pk):
    bus = Bus.bus.get(id=pk)
    form = BusForm(instance=bus)
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form}
    return render(request, 'bus_signals/bus_form.html', context)


def delete_bus(request, pk):
    bus = Bus.bus.get(id=pk)
    if request.method == 'POST':
        bus.delete()
        return redirect('bus_list')
    context = {'object': bus}
    return render(request, 'delete_object.html', context)



def bus_detail(request, pk):
    bus = Bus.bus.get(pk=pk)
    context = {'bus': bus}
    return render(request, 'bus_signals/bus_detail.html', context)


def bus_list(request):
    buses = Bus.bus.all()
    context = {'bus': buses}
    return render(request, 'bus_signals/bus_list.html', context)


def dic_fusi(request):
    return render(request, 'bus_signals/dic_fusi.html')


def odometer(request):
    return render(request, 'bus_signals/odometer.html')
