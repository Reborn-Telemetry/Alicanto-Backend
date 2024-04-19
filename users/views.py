from django.shortcuts import render
from bus_signals.models import Bus, ChargeStatus
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


def energy_record(request):
    days_of_month = range(1, 32) 
    lista_datos_organizados = [] 
    for y in Bus.bus.all():
        charge_data = ChargeStatus.charge_status.filter(bus_id=y.id).order_by('TimeStamp')

        rangos = []
        rango_actual = []

        for item in charge_data:
            if item.charge_status_value == 1:
                rango_actual.append(item)
            elif item.charge_status_value == 0:
                if rango_actual:
                    rangos.append(rango_actual.copy())
                    rango_actual.clear()
            else:
                continue

    # Agregar el último rango si no termina con Estado 0.0
        if rango_actual:
            rangos.append(rango_actual)

        santiago_tz = pytz.timezone('Chile/Continental')
        

    # Preparar los datos para la tabla y calcular acumulados
        datos_tabla = []
        for i, rango in enumerate(rangos, 1):
            fecha_inicio = rango[0].TimeStamp.strftime("%Y-%m-%d %H:%M:%S")
            fecha_termino = rango[-1].TimeStamp.strftime("%Y-%m-%d %H:%M:%S")
            soc_inicial = rango[0].soc_level
            soc_final = rango[-1].soc_level
            carga = soc_final - soc_inicial  # Resta de soc_level

            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S')
            fecha_termino_dt = datetime.strptime(fecha_termino, '%Y-%m-%d %H:%M:%S')

            fecha_inicio_dt_santiago = fecha_inicio_dt.replace(tzinfo=pytz.utc).astimezone(santiago_tz)
            fecha_termino_dt_santiago = fecha_termino_dt.replace(tzinfo=pytz.utc).astimezone(santiago_tz)

        # Calcular la diferencia de tiempo en horas
            diferencia = fecha_termino_dt_santiago - fecha_inicio_dt_santiago
            diferencia_en_horas = diferencia.total_seconds() / 3600

            datos_tabla.append({
                'rango': i,
                'fecha_inicio': fecha_inicio_dt_santiago.strftime("%Y-%m-%d %H:%M:%S"),
                'fecha_termino': fecha_termino_dt_santiago.strftime("%Y-%m-%d %H:%M:%S"),
                'tiempo': round(diferencia_en_horas, 2),
                'soc_inicial': soc_inicial,
                'soc_final': soc_final,
                'carga': carga,
                'energia': (carga * 140) / 100,
                'bus': y.bus_name
            })

        acumulado_mensual = {str(month).zfill(2): 0 for month in range(1, 13)}  

        fecha_actual = datetime.now()

        # Obtener el primer día del mes y el último día del mes actual
        primer_dia_mes = datetime(fecha_actual.year, fecha_actual.month, 1)
        ultimo_dia_mes = datetime(fecha_actual.year, fecha_actual.month + 1, 1) - timedelta(days=1)

    # Crear una lista con todas las fechas del mes
        dias_mes = [primer_dia_mes + timedelta(days=d) for d in range((ultimo_dia_mes - primer_dia_mes).days + 1)]

    # Inicializar la tabla de energía con todas las fechas del mes y energía total en cero
        tabla_energia = [{'bus':y.bus_name, 'fecha': fecha.strftime('%Y-%m-%d'), 'energia_total': 0} for fecha in dias_mes]
        complete_table = []

    # Actualizar la energía total en la tabla con los valores calculados
        for item in tabla_energia:
            for dato in datos_tabla:
                if dato['fecha_inicio'][:10] == item['fecha']:
                    item['energia_total'] += (dato['carga'] * 140) / 100
        
    
    
        for item in tabla_energia:
                bus = item['bus']
                fecha = item['fecha']
                energia_total = item['energia_total']

                bus_existe = False
                for datos_bus in lista_datos_organizados:
                    if datos_bus['bus'] == bus:
                        energia_total_formateada = "{:.1f}".format(energia_total)
                        datos_bus['datos'].append({'fecha': fecha, 'energia_total': energia_total_formateada})
                        bus_existe = True
                        break
                if not bus_existe:
                    lista_datos_organizados.append({'bus': bus, 'datos': [{'fecha': fecha, 'energia_total': round(energia_total,2)}]})
                
                context = {'lista_datos_organizados': lista_datos_organizados, 'days_of_month': days_of_month}

    # Imprimir la tabla de energía completa para el mes actual

    return render(request, 'reports/energy-record.html', context)