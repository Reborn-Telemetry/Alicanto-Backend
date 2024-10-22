from django.shortcuts import render
from bus_signals.models import Bus, ChargeStatus, Odometer
from bus_signals.query_utils import obtener_ultimo_valor_energia
from django.db.models import F, Max, Window
from django.db.models.functions import ExtractMonth, ExtractDay
# Create your views here.
from django.shortcuts import render, redirect
from bus_signals.forms import WorkOrderForm
from .models import WorkOrder, Profile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pytz
from django.utils import timezone
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import F, Case, When, IntegerField, Window
from django.db.models.functions import RowNumber
from itertools import groupby
no_update_list = [ '27','34', '60', '24', '87', '116', '21', '61', '82', '83', '81', '87', '137', '132', '134', '133', '130', '129', '128', '131', '136', '135' ]
# Create your views here.
@login_required(login_url='login')
def profile(request):
    workers = Profile.objects.all()
    context = {'workers': workers}
    return render(request, 'users/profile.html', context)

@login_required(login_url='login')
def work_order(request):
    return render(request, 'users/work_order_form.html')

@login_required(login_url='login')
def create_work_order(request):
    form = WorkOrderForm()
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form}
    return render(request, 'users/work_order_form.html', context)

@login_required(login_url='login')
def update_ot(request, pk):
    ot = WorkOrder.objects.get(id=pk)
    form = WorkOrderForm(instance=ot)
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, request.FILES, instance=ot)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form}
    return render(request, 'users/work_order_form.html', context)

def format_date(date):
    return date.strftime('%d/%m/%Y')  # Formato: día/mes/año

