from django.shortcuts import render, redirect
from .models import Bus, FusiMessage, Odometer
from .forms import BusForm, FusiMessageForm
from users.models import WorkOrder
from .query_utils import daily_bus_km, monthly_bus_km
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


# Create your views here.

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            print('User does not exist')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('bus_list')
        else:
            print('Username or password is incorrect')

    return render(request, 'login.html')

@login_required(login_url='login')
def create_bus(request):
    form = BusForm()
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form}
    return render(request, 'bus_signals/bus_form.html', context)

@login_required(login_url='login')
def create_fusi(request):
    form = FusiMessageForm()
    if request.method == 'POST':
        form = FusiMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dic_fusi')
    context = {'form': form}
    return render(request, 'bus_signals/fusi_form.html', context)

@login_required(login_url='login')
def update_bus(request, pk):
    bus = Bus.bus.get(id=pk)
    form = BusForm(instance=bus)
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES, instance=bus)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form}
    return render(request, 'bus_signals/bus_form.html', context)

@login_required(login_url='login')
def update_fusi(request, pk):
    message = FusiMessage.fusi.get(id=pk)
    form = FusiMessageForm(instance=message)
    if request.method == 'POST':
        form = FusiMessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('dic_fusi')
    context = {'form': form}
    return render(request, 'bus_signals/fusi_form.html', context)

@login_required(login_url='login')
def delete_bus(request, pk):
    bus = Bus.bus.get(id=pk)
    if request.method == 'POST':
        bus.delete()
        return redirect('bus_list')
    context = {'object': bus}
    return render(request, 'delete_object.html', context)

@login_required(login_url='login')
def bus_detail(request, pk):
    montly_result = monthly_bus_km(pk)
    results = daily_bus_km(pk)
    ot = WorkOrder.objects.filter(bus=pk)
    bus = Bus.bus.get(pk=pk)
    context = {'bus': bus, 'ot': ot, 'results': results, 'monthly_result': montly_result}
    return render(request, 'bus_signals/bus_detail.html', context)

@login_required(login_url='login')
def bus_list(request):
    buses = Bus.bus.all()
    context = {'bus': buses}
    return render(request, 'bus_signals/bus_list.html', context)

@login_required(login_url='login')
def dic_fusi(request):
    messages = FusiMessage.fusi.all()
    context = {'fusi': messages}
    return render(request, 'bus_signals/dic_fusi.html', context)

@login_required(login_url='login')
def odometer(request):
    return render(request, 'bus_signals/odometer.html')
