from django.shortcuts import render, redirect

from reports.views import switch_report_xls
from .models import Bus, FusiMessage, Odometer, FusiCode, BatteryHealth, Isolation, ChargeStatus, CellsVoltage, Speed, EcuState
from users.models import WorkOrder
from .forms import BusForm, FusiMessageForm, FusiForm
from .query_utils import daily_bus_km, format_date, monthly_bus_km, monthly_fleet_km, get_max_odometer_per_month, km_flota, get_battery_health_report
import requests
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Max, F, Avg
# pdf imports 
from django.http import FileResponse, HttpResponse
import io
from reportlab.platypus import Spacer
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.http import FileResponse
from reportlab.lib.pagesizes import letter, landscape
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
import xlwt
from io import BytesIO
# manejo errores paginador
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import pytz
from collections import defaultdict
from services.fs_link import fs_link_api


filter_fusi_code = [ 21004.0, 20507.0, 20503.0, 20511.0, 20509.0, 20498.0, 20506.0, 20525.0,
                     16911.0, 20519.0, 20499.0, 20505.0, 20502.0, 21777.0, 21780.0, 20500.0, 
                     20508.0, 20510.0, 20504.0, 20520.0, 20515.0, 20501.0 ]

no_update_list = [ '27','34', '60', '24', '87', '116', '21', '61', '82', '83',
                   '81', '87', '137', '132', '134', '133', '130', '129', '128', '131', '136', '135' ]

@login_required(login_url='login')
def no_access(request):
    return render(request, 'pages/no-access.html')


@login_required(login_url='login')
def warnings(request):
    bus_instance = Bus()
    delayed = bus_instance.delay_data().exclude(id__in=no_update_list)
    low_50_soc_records = Bus.bus.filter(lts_soc__lt=50).exclude(id__in=no_update_list)
    low_50_soc_count = low_50_soc_records.all().exclude(lts_soc=0.0)
    low_50 = list(low_50_soc_count.values('bus_name', 'lts_soc'))
    top_buses = FusiCode.fusi.values('bus__bus_name').annotate(num_registros=Count('bus')).order_by('-num_registros')[:10]
    no_update = Bus.bus.filter(lts_update=None)
    no_update = no_update.exclude(id__in=no_update_list)
    low_battery = Bus.bus.filter(lts_24_volt__lt=20)
    low_battery = low_battery.exclude(lts_24_volt=0.0)
    low_24_grafico = list(low_battery.values('bus_name', 'lts_24_volt'))
     # fusicodes monthly
    current_month = timezone.now().month
    distinct_fusi_code = FusiCode.fusi.filter(TimeStamp__month=current_month).values('fusi_code').annotate(total=Count('fusi_code')).order_by('-total')
    distinct_fusi_code = distinct_fusi_code.exclude(fusi_code__in=filter_fusi_code)
    fusi_grafico = list(distinct_fusi_code.values('fusi_code', 'total'))
    top_grafico = list(top_buses.values('bus__bus_name', 'num_registros'))

    current_datetime = timezone.now()
    mes_actual = current_datetime.strftime('%B')


    # paginador buses sin conexion
    page = request.GET.get('page')
    results = 10
    paginator_no_update = Paginator(no_update, results)

    try:
        no_update = paginator_no_update.page(page)
    except PageNotAnInteger:
        page = 1
        no_update = paginator_no_update.page(page)
    except EmptyPage:
        page = paginator_no_update.num_pages
        no_update = paginator_no_update.page(page)
    # fin paginador buses sin conexion
    # inicio paginador delayed
    page2 = request.GET.get('page2')
    results2 = 10
    paginator_delayed = Paginator(delayed, results2)

    try:
        delayed = paginator_delayed.page(page2)
    except PageNotAnInteger:
        page2 = 1
        delayed = paginator_delayed.page(page2)
    except EmptyPage:
        page2 = paginator_delayed.num_pages
        delayed = paginator_delayed.page(page2)

    # fin paginador delayed
 
        
         # paginador fusi
    page_fusi = request.GET.get('page_fusi')
    results_fusi = 10
    paginator_fusi = Paginator(distinct_fusi_code, results_fusi)
    try:
        distinct_fusi_code = paginator_fusi.page(page_fusi)
    except PageNotAnInteger:
        page_fusi = 1
        distinct_fusi_code = paginator_fusi.page(page_fusi)
    except EmptyPage:
        page_fusi = paginator_fusi.num_pages
        distinct_fusi_code = paginator_fusi.page(page_fusi)

    # speed table
    speed_records = Speed.speed.filter(speed_value__gt=39)
    speed_records = speed_records.select_related('bus').order_by('-TimeStamp')[:50]
    
    context = {
        'top_grafico': top_grafico,
        'low_24_grafico': low_24_grafico,
        'fusi_grafico': fusi_grafico,
        'mes_actual': mes_actual,
        'low_battery': low_battery,
        'no_update': no_update,
        'delayed': delayed,
        'low_50_soc_count': low_50_soc_count,
        'paginator_no_update': paginator_no_update,
        'paginator_delayed': paginator_delayed,
        'top_buses': top_buses,
        'distinct_fusi_code': distinct_fusi_code,
        'paginator_fusi': paginator_fusi,
        'low_50':low_50,
        'speed_records': speed_records,
    }
    return render(request, 'pages/warnings.html', context)


@login_required(login_url='login')
def reports_page(request):
    
    bus = Bus.bus.all()
    bus = bus.exclude(id__in=no_update_list)

    page = request.GET.get('page', 1)
    results = 10
    paginator = Paginator(bus, results)
    try:
        bus = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        bus = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        bus = paginator.page(page)
    context = {
        'bus': bus,
        'paginator': paginator}
    return render(request, 'reports/reports.html', context)

@login_required
def fusi_dashboard(request):
    open_fusi = FusiCode.fusi.all().exclude(fusi_state='Cerrado')
    open_fusi = open_fusi.exclude(fusi_code__in=filter_fusi_code)
    page = request.GET.get('page')
    results = 30
    paginator = Paginator(open_fusi, results)
    try:
        open_fusi = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        open_fusi = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        open_fusi = paginator.page(page)

    context = {'active_fusi': open_fusi, 'paginator': paginator}
    return render(request, 'fusi/fusi-dashboard.html', context)


@login_required(login_url='login')
def bus_list_view(request):
    search_query = ''
    page = request.GET.get('page')
    results = 9

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
    buses = Bus.bus.filter(
        Q(bus_name__icontains=search_query) |
        Q(bus_series__icontains=search_query) |
        Q(bus_ecu__icontains=search_query) |
        Q(client__icontains=search_query)
    )

    paginator = Paginator(buses, results)
    try:
        buses = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        buses = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        buses = paginator.page(page)

    context = {'bus': buses, 'search_query': search_query, 'paginator': paginator}
    return render(request, 'bus/bus_list_view.html', context)


@login_required(login_url='login')
def bus_list(request):
    search_query = ''
    page = request.GET.get('page')
    results = 9

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
    buses = Bus.bus.filter(
        Q(bus_name__icontains=search_query) |
        Q(bus_series__icontains=search_query) |
        Q(bus_ecu__icontains=search_query) |
        Q(client__icontains=search_query)
    )

    paginator = Paginator(buses, results)
    try:
        buses = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        buses = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        buses = paginator.page(page)

    context = {'bus': buses, 'search_query': search_query, 'paginator': paginator}
    return render(request, 'bus/bus-list.html', context)


@login_required(login_url='login')
def bus_detail(request, pk):
    montly_result = monthly_bus_km(pk)
    results = daily_bus_km(pk)
    months_dict = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre',
}

    result_data = []

# Obtener el mes actual
    current_month = datetime.now().month

# Iterar sobre el rango correcto para cada mes
    if montly_result and len(montly_result[0]) > 0:
    # Iterar sobre todos los meses
        for month in range(1, 13):
         index = (month - 1) * 2 + 1  # Calcular el índice correspondiente en los resultados
         if index < len(montly_result[0]):
            value1 = montly_result[0][index]
            value2 = montly_result[0][index + 1] if index + 1 < len(montly_result[0]) else None
            difference = value2 - value1 if value2 is not None else None

            # Si el mes es el actual y solo hay un valor disponible (value1), indicar que está en curso
            if month == current_month and value2 is None:
                result_data.append({
                    'month': months_dict[month],
                    'value1': value1,
                    'value2': 'En curso',
                    'difference': 'Calculando'
                })
            elif value1 is not None and value2 is not None:
                result_data.append({
                    'month': months_dict[month],
                    'value1': value1,
                    'value2': value2,
                    'difference': difference if difference is not None else 'Calculando'
                })
            else:
                result_data.append({
                    'month': months_dict[month],
                    'value1': 0,
                    'value2': 0,
                    'difference': 0
                })
        else:
            result_data.append({
                'month': months_dict[month],
                'value1': 0,
                'value2': 0,
                'difference': 0
            })
    else:
    # Si no hay resultados, agregar todos los meses con ceros
        for month in range(1, 13):
            result_data.append({
            'month': months_dict[month],
            'value1': 0,
            'value2': 0,
            'difference': 0
        })
            
    

    #calculo de 
    
    ot = WorkOrder.objects.filter(bus=pk)
    bus = Bus.bus.get(pk=pk)

    soh = 0
    try:
     latest_battery_health = BatteryHealth.battery_health.filter(bus_id=pk).latest('battery_health_value')
     soh = latest_battery_health
    except ObjectDoesNotExist:
     print('No se encontraron registros en BatteryHealth para el bus_id especificado.')

    messages = FusiMessage.fusi.all()
    fusi_codes = FusiCode.fusi.filter(bus_id=pk).order_by('-TimeStamp')[:600]
    for code in fusi_codes:
        for fusi_message in messages:
            if code.fusi_code == fusi_message.fusi_code:
                code.fusi_description = fusi_message.fusi_description
                break

    co2 = 0  # Valor predeterminado en caso de que bus.lts_odometer sea None
    if bus.lts_odometer is not None and bus.bus_series == 'Tricahue':
        co2 = (bus.lts_odometer * 857) / 1000
        co2 /= 1000  # Dividir nuevamente para obtener el resultado correcto
        co2 = round(co2, 2)
    else: 
        co2 = (bus.lts_odometer * 443) / 1000
        co2 /= 1000
        co2 = round(co2, 2)

    fusi_grafico = FusiCode.fusi.filter(bus_id=pk).values('fusi_code').annotate(total=Count('fusi_code')).order_by('-total')
    fusi_grafico2 = list(fusi_grafico.values('fusi_code', 'total'))

    isolation = Isolation.isolation.filter(bus_id=pk).values('isolation_value')[:40]
    isolation2 = list(isolation.values('isolation_value'))
    # paginador fusi
    page = request.GET.get('page')
    result = 15
    paginator = Paginator(fusi_codes, result)
    try:
        fusi_codes = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        fusi_codes = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        fusi_codes = paginator.page(page)
# bitacora de carga comienzo ----------------------------------------------------------------------->
    current_datetime = timezone.now()
    mes_actual = current_datetime.strftime('%m')

    charge_data = ChargeStatus.charge_status.filter(bus_id=pk).order_by('TimeStamp')

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
            'energia': (carga * 140) / 100 if bus.bus_series == 'Queltehue' else (carga * 280) / 100,
})

    acumulado_mensual = {str(month).zfill(2): 0 for month in range(1, 13)}  

    
    for i in datos_tabla:
        fecha_inicio = i['fecha_inicio']

    # fecha_inicio is in the format "YYYY-MM-DD HH:MM:SS"
        try:
            month = fecha_inicio[5:7]  # Extract month as a string
            acumulado_mensual[month] += i['energia']
        except ValueError:
        # Handle invalid month format (e.g., log or skip entry)
            print(f"Invalid month format found in fecha_inicio: {fecha_inicio}")
            pass

    monthly_totals = []
    for month, energy in acumulado_mensual.items():
        monthly_totals.append({'month': month, 'energy': round(energy, 2)})

    
    acu = round(sum(i['energia'] for i in datos_tabla), 2)


    cells_voltage = CellsVoltage.cells_voltage.filter(bus_id=pk).order_by('-TimeStamp')[:100]
    #tabla de rendimiento
    monthly_totals_dict = {item['month']: item['energy'] for item in monthly_totals}

# Combinar ambas listas en una nueva lista para rendimiento ----------------------------------->
    month_name_to_number = {
    'Enero': '01',
    'Febrero': '02',
    'Marzo': '03',
    'Abril': '04',
    'Mayo': '05',
    'Junio': '06',
    'Julio': '07',
    'Agosto': '08',
    'Septiembre': '09',
    'Octubre': '10',
    'Noviembre': '11',
    'Diciembre': '12'
}
    combined_data = []
    calc_rendimiento = lambda energy, diff: round(float(energy) / float(diff), 2) if diff and energy and isinstance(diff, (int, float)) and isinstance(energy, (int, float)) else None


    for item in result_data:
        month_name = item['month']
        month_number = month_name_to_number[month_name]
        energy = float(monthly_totals_dict.get(month_number, 0))
    
        difference = item['difference']
        if isinstance(difference, str) or difference == 0:
            difference = None  # O manejar de otra forma, dependiendo de la lógica de negocio

        combined_data.append({
            'month': month_name,
            'difference': difference,
            'energy': energy,
            'rendimiento': calc_rendimiento(energy, difference)
        })

# Ahora 'combined_data' tiene la combinación de ambas listas

    context_perfil = {
               'bus': bus,
               'message': messages,
               'ot': ot, 
               'results': results,
               'monthly_result': montly_result,
               'fusi': fusi_codes,
               'result_data': result_data, 
               'co2': co2, 
               'paginator': paginator,
               'soh': soh,
               'fusi_pie': fusi_grafico2,
               'isolation': isolation2,
               'datos_tabla': datos_tabla,
               'acu': acu,
               'monthly_totals': monthly_totals,
               'cells_voltage': cells_voltage,
               'rendimiento': combined_data,
                
                }
    return render(request, 'bus/bus-profile.html', context_perfil)

@login_required(login_url='login')
def dashboard(request):
    #-----------------------------------------------------------------------------
    # API Link
    data = fs_link_api()
    cant_fs = (data['cant_fs'])
    fs_vehicles = data['data']
     # buses en Operacion
    operacion = total_flota - cant_fs
    
    #-----------------------------------------------------------------------------------------------------------
    # cantidad de buses en la flota
    #optimizada
    total_flota = total_flota = Bus.bus.filter(~Q(id__in=no_update_list)).aggregate(total=Count('id'))['total']
    
    #---------------------------------------------------------------------------------------------
    # datos tabla de buses
    # optimizada
    #complete_table = Bus.bus.exclude(lts_update=None).order_by('-lts_update').values(
     #   'id','bus_name','lts_soc','lts_odometer','lts_isolation','lts_24_volt','lts_fusi',
     #   'charging','lts_update','key_state','ecu_state','bus_series')
    # paginador tabla
    #page = request.GET.get('page', 1)
    #results = 7
    #paginator = Paginator(complete_table, results)
    #try:
     #   complete_table = paginator.page(page)
    #except PageNotAnInteger:
     #   page = 1
     #   complete_table = paginator.page(page)
    #except EmptyPage:
     #   page = paginator.num_pages
      #  complete_table = paginator.page(page)
    #-----------------------------------------------------------------------------------------------

    # km total de la flota
    # optimizado
    #km_total = Bus.bus.annotate(max_odometer=Max
     #                           ('odometer__odometer_value')).aggregate(
      #                              total_km=Sum('max_odometer'))['total_km'] or 0  
    
#-----------------------------------------------------------------------------------------------------
    # co2 ahorrado total flota
    # optimizada
  
   # co2_total = round(km_total * 0.00067, 2)

#-------------------------------------------------------------------------------------------------------

    # menor 50 optimizada
    # cantidad de buses con soc menor a 50
    #cant_low_50_soc = low_50_soc_count = Bus.bus.filter(lts_soc__lt=50).exclude(lts_soc=0.0).count()

#------------------------------------------------------------------------------------------------------    
    # cantidad buses con cola de archivos
    #optimizada
    #bus_instance = Bus()
    #delayed = bus_instance.delay_data().exclude(id__in=no_update_list).count()


# -------------------------------------------------------------------------------------------------------
   

    
#---------------------------------------------------------------------------------------------------------
# inicio codigo grafico fusi
#optimizada
    #current_month = timezone.now().month
    #distinct_fusi_code = (
     #   FusiCode.fusi
      #  .filter(TimeStamp__month=current_month)
       # .exclude(fusi_code__in=filter_fusi_code)
        #.values('fusi_code')
        #.annotate(total=Count('fusi_code'))
        #.order_by('-total')
    #)

    #fusi_grafico = list(distinct_fusi_code) 
# fin codigo grafico fusi
#-------------------------------------------------------------------------------------------------------

# inicio codigo kwh anual
    #total_per_month = defaultdict(int)
    #charging = 0

# Iterar sobre todos los buses y sus datos de odómetro
    #for bus in Bus.bus.only('id'):
    # Obtener el dict de máximo odómetro por mes para el bus actual
     #   max_values_per_month = get_max_odometer_per_month(bus.id)
      #  if bus.charging == 1:
       #     charging += 1
    # Iterar sobre cada mes en el dict y sumar el valor al total correspondiente
        #for month, max_value in max_values_per_month.items():
         #total_per_month[month] += max_value
# Final codigo kwh anual
    
    # grafico co2 evitado 
    #linechart_data = []
    #linechart_data2 = []
    #for month, total in total_per_month.items():
     #   linechart_data.append({'month': month, 'total': round(total * 0.00067)})
      #  linechart_data2.append({'month': month, 'total': round(total * 0.0004187)})

    """# energia total cargada año
    energia_anual = 0
    for i in Bus.bus.all():
        charge_data = ChargeStatus.charge_status.filter(bus_id=i.id).order_by('TimeStamp')

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
            })

        acumulado_mensual = {str(month).zfill(2): 0 for month in range(1, 13)}  

    
        for i in datos_tabla:
            fecha_inicio = i['fecha_inicio']

    # Assuming fecha_inicio is in the format "YYYY-MM-DD HH:MM:SS"
            try:
                month = fecha_inicio[5:7]  # Extract month as a string
                acumulado_mensual[month] += i['energia']
            except ValueError:
        # Handle invalid month format (e.g., log or skip entry)
                print(f"Invalid month format found in fecha_inicio: {fecha_inicio}")
                pass

        monthly_totals = []
        for month, energy in acumulado_mensual.items():
            monthly_totals.append({'month': month, 'energy': round(energy, 2)})

        
        acu = round(sum(i['energia'] for i in datos_tabla), 2)
        energia_anual += acu
        energia_anual = round(energia_anual)
        request.session['energia_anual'] = round(energia_anual)"""

    
       # request.session['charging'] = charging

    context = {
       
        'operacion': operacion,
        #'km_total': km_total,
        #'low_50_soc_count': low_50_soc_count,
        'total_flota': total_flota,
        #'bus': complete_table,
        #'cant_low_50_soc': cant_low_50_soc,
        #'delayed': delayed,
        #'paginator': paginator,
        'cant_fs': cant_fs,
        #'co2_total': co2_total,
       # 'fusi_grafico': fusi_grafico,
        #'linechart_data': linechart_data,
        #'linechart_data2': linechart_data2,
        #'charging': charging,
        #'energia_anual': energia_anual,
        #'fs_vehicles': fs_vehicles,
    }
    return render(request, 'pages/dashboard.html', context)

@login_required
def monthly_bus_report_xls(request):
    report_data = monthly_fleet_km()
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte km mensual :{formatted_datetime}.xls'
    buf = io.BytesIO()

    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('Report')

    table_data = [
        ['Bus', 'Ene I', 'Ene F', 'Feb I', 'Feb F', 'Mar I', 'Mar F', 'Abr I', 'Abr F',
         'May I', 'May F', 'Jun I', 'Jun F', 'Jul I', 'Jul F', 'Ago I', 'Ago F',
         'Sep I', 'Sep F', 'Oct I', 'Oct F', 'Nov I', 'Nov F', 'Dic I', 'Dic F']
    ]

    for entry in report_data:
        row = [str(value) if value is not None else '0' for value in entry]
        table_data.append(row)

    style = xlwt.easyxf('font: bold on; align: horiz center')

    for row_num, row_data in enumerate(table_data):
        for col_num, cell_value in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_value, style)

    workbook.save(buf)
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=filename)

@login_required
def monthly_bus_report(request):
    report_data = monthly_fleet_km()
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte km mensual :{formatted_datetime}.pdf'
    buf = io.BytesIO()

    doc = SimpleDocTemplate(buf, pagesize=landscape(letter))
    elements = []

    table_data = [[
        
            'Bus', 'Ene I', 'Ene F', 'Feb I', 'Feb F', 'Mar I', 'Mar F', 'Abr I', 'Abr F',
            'May I', 'May F', 'Jun I', 'Jun F', 'Jul I', 'Jul F', 'Ago I', 'Ago F',
            'Sep I', 'Sep F', 'Oct I', 'Oct F', 'Nov I', 'Nov F', 'Dic I', 'Dic F'
        ]
    ]

    for entry in report_data:
        row = []
        for value in entry:
            row.append(str(value) if value is not None else '0')
        table_data.append(row)

    cell_width = 17
    font_size = 5
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), 'white'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), 'lightgrey'),
        ('BOX', (0, 0), (-1, -1), 1, 'black'),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
    ])

    table = Table(table_data, colWidths=[cell_width * 1.5] * len(table_data[0]))
    table.setStyle(style)
    elements.append(table)

    image_path = 'static/img/REM.png'
    image_width = 150
    image_height = 150
    image = Image(image_path, width=image_width, height=image_height)
    elements.insert(0, image)

    doc.build(elements)

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)

@login_required
def software_version(request):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte versiones software :{formatted_datetime}.xls'
    buf = io.BytesIO()

    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('Report')

    table_data = [[
        'Bus', 'Mark', 'Jarvis', 'Vision', 'Fecha de actualización'
    ]]
    buses = Bus.bus.all()

    for i in buses:
        formatted_datetime = i.lts_update.strftime("%d/%m/%Y %H:%M") if i.lts_update else "sin actualizacion"
        row = [
            i.bus_name, i.mark, i.jarvis, i.vision, formatted_datetime
               ]
        table_data.append(row)
    
    style = xlwt.easyxf('font: bold on; align: horiz center')
    for row_num, row_data in enumerate(table_data):
        for col_num, cell_value in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_value, style)

    workbook.save(buf)
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=filename)

@login_required
def xls_report(request):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte dia :{formatted_datetime}.xls'
    buf = io.BytesIO()

    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('Report')

    table_data = [
        ["Bus", "Sniffer", "Carga", "Kiometraje", "Fecha de actualizacion"]
    ]

    bus_list = Bus.bus.all()
    for bus in bus_list:
        formatted_datetime = bus.lts_update.strftime("%d/%m/%Y %H:%M") if bus.lts_update else "sin actualizacion"
        row = [bus.bus_name, bus.sniffer, str(bus.lts_soc), str(bus.lts_odometer), formatted_datetime]
        table_data.append(row)

    style = xlwt.easyxf('font: bold on; align: horiz center')

    for row_num, row_data in enumerate(table_data):
        for col_num, cell_value in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_value, style)

    workbook.save(buf)
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=filename)

@login_required(login_url='login')
def recorrido_mensual_flota(request):
    buses = Bus.bus.all()
    buses = buses.exclude(id__in=no_update_list)
    elements = []
    
    for bus in buses:
        result = monthly_bus_km(bus.id)
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%m-%Y")
        filename = f'reporte_recorrido_mensual_flota_{formatted_datetime}.pdf'
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        table_data = [['Bus', 'Mes', 'Kilometraje Inicial', 'Kilometraje Final', 'Recorrido']]
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        idx_mes = 0
        for item in result:
            # Ignorar el primer valor de la tupla
            item = item[1:]
            for i in range(len(item)):
                if i % 2 == 0:  # Índices impares para kilómetros iniciales
                    mes = meses[idx_mes]
                    km_inicial = item[i]
                    km_final = item[i + 1] if i + 1 < len(item) else None
                    recorrido = km_final - km_inicial if km_final is not None else ''
                    # Aquí se agrega el nombre del bus en lugar del ID
                    table_data.append([bus.bus_name, mes, km_inicial, km_final, recorrido])
                    idx_mes += 1  # Avanzar al siguiente mes
        
        # Estilo de la tabla
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('LINEBELOW', (0, 1), (-1, -1), 1, colors.black)
        ])
        
        # Crear la tabla y aplicar el estilo
        spacer = Spacer(0, 20)
        table = Table(table_data)
        table.setStyle(style)
        elements.append(table)
        elements.append(spacer)
        
        
       
    # Construir el documento y guardar en el buffer
    image_path = 'static/img/REM.png'
    image = Image(image_path, width=80, height=80)
    elements.insert(0, image)

    doc.build(elements)
    
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)

@login_required(login_url='login')
def recorrido_mensual_bus_pdf(request, pk):
    bus = Bus.bus.get(id=pk)
    result = monthly_bus_km(pk)
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte_recorrido_mensual bus {bus.bus_name}_{formatted_datetime}.pdf'
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    elements = []

    # Crear la tabla con los datos de los meses y el recorrido
    table_data = [['Mes', 'Kilometraje Inicial', 'Kilometraje Final', 'Recorrido']]
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    idx_mes = 0  # Índice para recorrer los meses
    for item in result:
        # Ignorar el primer valor de la tupla
        item = item[1:]
        for i in range(len(item)):
            if i % 2 == 0:  # Índices impares para kilómetros iniciales
                mes = meses[idx_mes]
                km_inicial = item[i]
                km_final = item[i + 1] if i + 1 < len(item) else None
                recorrido = km_final - km_inicial if km_final is not None else ''
                table_data.append([mes, km_inicial, km_final, recorrido])
                idx_mes += 1  # Avanzar al siguiente mes

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('LINEBELOW', (0, 1), (-1, -1), 1, colors.black)
    ])

    # Crear la tabla y aplicar el estilo
    table = Table(table_data)
    table.setStyle(style)
    elements.append(table)

    image_path = 'static/img/REM.png'
    image = Image(image_path, width=80, height=80)
    elements.insert(0, image)

    # Construir el documento y guardar en el buffer
    doc.build(elements)

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)

@login_required(login_url='login')
def bus_historic_fusi(request, pk):
    bus = Bus.bus.get(id=pk)
    fusi_bus = FusiCode.fusi.filter(bus_id=pk).values('fusi_code').annotate(total=Count('fusi_code'))
    fusi_bus_complete = FusiCode.fusi.filter(bus_id=pk)
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte historico fusi_{bus.bus_name}_{formatted_datetime}.pdf'
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    elements = []
    table_data_2 = [['Fecha', 'Codigo Fusi', 'Kilometraje Ocurrencia']]
    table_data = [
        ["Codigo Fusi", "Ocurrencias"]
    ]
    for item in fusi_bus:
        table_data.append([item['fusi_code'], item['total']])
    
    for item2 in fusi_bus_complete:
        table_data_2.append([item2.TimeStamp.strftime("%d-%m-%Y %H:%M"), int(item2.fusi_code), item2.failure_odometer ])

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), 'grey'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), 'lightgrey'),
        ('LINEBELOW', (0, 1), (-1, -1), 1, 'black')
    ])

    # Crear la tabla y aplicar el estilo
    table = Table(table_data)
    table2 = Table(table_data_2)
    table2.setStyle(style)
    table.setStyle(style)
    spacer = Spacer(0, 20)
    elements.append(table)
    elements.append(spacer)
    elements.append(table2)
    
    image_path = 'static/img/REM.png'
    image = Image(image_path, width=80, height=80)
    elements.insert(0, image)

    doc.build(elements)

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)
    
@login_required
def pdf_report(request):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte dia :{formatted_datetime}.pdf'
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    elements = []

    table_data = [
        ["Bus", "Sniffer", "Ultimo SOC", "Ultimo Odometro", "Fecha de actualizacion"]
    ]

    bus_list = Bus.bus.all()
    for bus in bus_list:
        formatted_datetime = bus.lts_update.strftime("%d/%m/%Y %H:%M") if bus.lts_update else "sin actualizacion"
        row = [bus.bus_name, bus.sniffer, str(bus.lts_soc), str(bus.lts_odometer) + 'km', formatted_datetime]
        table_data.append(row)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), 'grey'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), 'lightgrey'),
    ])

    table = Table(table_data)
    table.setStyle(style)
    elements.append(table)

    image_path = 'static/img/REM.png'
    image = Image(image_path, width=80, height=80)
    elements.insert(0, image)

    doc.build(elements)

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)

def login_page(request):
    if request.user.is_authenticated:
        return redirect('bus_list')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'El usuario no existe')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Ingresaste correctamente')
            return redirect('dashboard')
        else:
            messages.error(request, 'nombre de usuario o contraseña incorrectos')


           

    return render(request, 'pages/login.html')

@login_required
def logout_user(request):
    logout(request)
    messages.error(request, 'Sesion cerrada correctamente')

    return redirect('login')

@login_required(login_url='login')
def create_bus(request):
    form = BusForm()
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form}
    return render(request, 'bus/bus-form.html', context)

@login_required(login_url='login')
def create_fusi(request):
    form = FusiMessageForm()
    if request.method == 'POST':
        form = FusiMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dic_fusi')
    context = {'form': form}
    return render(request, 'fusi/fusi-form.html', context)


@login_required(login_url='login')
def update_bus(request, pk):
    bus = Bus.bus.get(id=pk)
    form = BusForm(instance=bus)
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES, instance=bus)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form, 'bus': bus}
    return render(request, 'bus/bus-form.html', context)


@login_required(login_url='login')
def update_fusicode(request, pk):
    fusi_code = FusiCode.fusi.get(id=pk)
    form = FusiForm(instance=fusi_code)
    if request.method == 'POST':
        form = FusiForm(request.POST, instance=fusi_code)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'fusi/fusicode-form.html', context)


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
    return render(request, 'fusi/fusi-form.html', context)


@login_required(login_url='login')
def delete_bus(request, pk):
    bus = Bus.bus.get(id=pk)
    if request.method == 'POST':
        bus.delete()
        return redirect('bus_list')
    context = {'object': bus}
    return render(request, 'pages/delete_object.html', context)


@login_required(login_url='login')
def dic_fusi(request):
    search_query = ''
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    messages = FusiMessage.fusi.filter(
        Q(fusi_code__icontains=search_query) |
        Q(fusi_description__icontains=search_query) |
        Q(message_class__icontains=search_query)
    )
    # paginadorfusi
    page = request.GET.get('page')
    results = 17
    paginator = Paginator(messages, results)
    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        messages = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        messages = paginator.page(page)
    # fin paginador fusi

    context = {
        'fusi': messages,
        'search_query': search_query,
        'paginator': paginator
    }
    return render(request, 'fusi/fusi-dictionary.html', context)


