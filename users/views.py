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

def energy_record(request):

    #----------buses cargando----------------------------------
 charging = request.session.get('charging')
 energia_anual = request.session.get('energia_anual')
    #---------------------------------------------------------
   
 bus_id = 1  # Cambia por el ID del bus que deseas filtrar
 mes = 10    # Cambia por el mes que deseas (número de mes)

# Obtener los registros de ChargeStatus filtrados por bus_id y mes, y ordenados por TimeStamp
 charge_statuses = ChargeStatus.charge_status.filter(bus_id=bus_id).annotate(
    mes=ExtractMonth('TimeStamp')
).filter(mes=mes).order_by('TimeStamp')

# Lista para almacenar ciclos de carga
 charge_cycles = []
 current_cycle = []


# Iterar sobre los registros y agrupar por ciclos continuos de valores 1
 for status in charge_statuses:
    if status.charge_status_value == 1:
        current_cycle.append(status)
    else:
        # Si no es 1, y tenemos un ciclo en curso, lo agregamos a la lista de ciclos
        if current_cycle:
            first_status = current_cycle[0]
            last_status = current_cycle[-1]
            soc_difference = last_status.soc_level - first_status.soc_level  # Diferencia de SOC

            charge_cycles.append({
                'fecha_inicio': format_date(first_status.TimeStamp),
                'fecha_final': format_date(last_status.TimeStamp),
                'diferencia_carga': soc_difference,
                'energia': soc_difference  # Si la energía es igual a la diferencia de carga
            })
            current_cycle = []  # Reiniciar el ciclo

# Agregar el último ciclo si terminó con un 1
 if current_cycle:
    first_status = current_cycle[0]
    last_status = current_cycle[-1]
    soc_difference = first_status.soc_level - last_status.soc_level  # Diferencia de SOC

    charge_cycles.append({
        'fecha_inicio': format_date(first_status.TimeStamp),
        'fecha_final': format_date(last_status.TimeStamp),
        'diferencia_carga': soc_difference,
        'energia': soc_difference  # Si la energía es igual a la diferencia de carga
    })

# La lista charge_cycles ahora contiene los diccionarios con la información de cada ciclo formateada
 for cycle in charge_cycles:
    print(cycle)
 context = {'charging': charging, 'energia_anual':energia_anual}

 return render(request, 'reports/energy-record.html', context)