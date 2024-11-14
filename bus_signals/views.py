import calendar
from django.shortcuts import render, redirect
import threading
from bus_signals.threads.energia_anual import calcular_energia_anual, calcular_energia_anual_diaria
from bus_signals.threads.recorridos import calcular_recorridos_por_dia
from reports.views import switch_report_xls
from .models import Bus, FusiMessage, Odometer, AnualEnergy, FusiCode, BatteryHealth, Isolation, ChargeStatus, CellsVoltage, Speed, EcuState
from users.models import WorkOrder
from .forms import BusForm, FusiMessageForm, FusiForm
from .query_utils import daily_bus_km, format_date, monthly_bus_km, monthly_fleet_km, get_max_odometer_per_month, km_flota, get_battery_health_report, get_monthly_kilometer_data
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
from django.db.models.functions import ExtractMonth, ExtractYear
from bus_signals.threads.matriz_energia_historico_flota import save_historical_energy_data
from bus_signals.threads.max_odometer_dayly import get_max_odometer_per_day_and_month
import locale


filter_fusi_code = [ 21004.0, 20507.0, 20503.0, 20511.0, 20509.0, 20498.0, 20506.0, 20525.0,
                     16911.0, 20519.0, 20499.0, 20505.0, 20502.0, 21777.0, 21780.0, 20500.0, 
                     20508.0, 20510.0, 20504.0, 20520.0, 20515.0, 20501.0 ]

no_update_list = ['83', '87', '137', '132', '134', '133', '130', '129', '128', '131', '136', '135' ]

@login_required(login_url='login')
def no_access(request):
    return render(request, 'pages/no-access.html')


@login_required(login_url='login')
def warnings(request):
    meses_es = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
    fecha_actual = timezone.now()
    mes_actual = fecha_actual.month
    nombre_mes = meses_es[mes_actual]
    

    cant_fusi_month = FusiCode.fusi.filter(TimeStamp__year = fecha_actual.year,TimeStamp__month = fecha_actual.month).count()
    km_total = request.session.get('km_total', 0)
    cant_low_50_soc = request.session.get('cant_low_50_soc', 0)
    delay = request.session.get('delay', 0)
    cant_fs = request.session.get('cant_fs, 0')
    total_flota = request.session.get('total_flota', 0)
    operacion = request.session.get('operacion', 0)
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
    low_24_cant = low_battery.count()
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
    results2 = 7
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
        'mes_actual': nombre_mes,
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
        'km_total' : km_total,
        'cant_low_50_soc': cant_low_50_soc, 
        'delay' : delay,
        'cant_fs': cant_fs,
        'low_24_cant': low_24_cant,
        'total_flota': total_flota,
        'operacion': operacion,
        'cant_fusi_month': cant_fusi_month
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
    fecha_actual = timezone.now()
    mes_actual = fecha_actual.month
    año_actual = fecha_actual.year
    #---------------------------------------------------------------
    meses_es = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 
    12: "Diciembre"
}
    #---------------------------------------------------------------
    total_fusi = FusiCode.fusi.count()
    #---------------------------------------------------------------
    nombre_mes = meses_es[mes_actual]
    #---------------------------------------------------------------
    cant_fusi_month = FusiCode.fusi.filter(
        TimeStamp__year = fecha_actual.year,
        TimeStamp__month = fecha_actual.month
        ).count()
    #-----------------------------------------------------------------------------
    baddest_bus = FusiCode.fusi.values('bus__bus_name') \
                                        .annotate(total_registros=Count('id')) \
                                        .order_by('-total_registros') \
                                        .first()
    baddest_bus_name = baddest_bus['bus__bus_name'] if baddest_bus else None
    total_badddest_bus_reg = baddest_bus['total_registros'] if baddest_bus else 0
    #-----------------------------------------------------------------------------
    worst_month = FusiCode.fusi.annotate(
    year=F('TimeStamp__year'),
    month=F('TimeStamp__month')
    ).values('year', 'month').annotate(
    total_registros=Count('id')
    ).order_by('-total_registros').first()
    if worst_month:
        worst_year = worst_month['year']
        worst_month_reg = worst_month['month']
        total_reg_worst = worst_month['total_registros']
    else:
        worst_year = None
        worst_month_reg = None
        total_reg_worst = 0
    worst_month_name = meses_es.get(worst_month_reg, "Mes desconocido")
    #--------------------------------------------------------------------------
    fusi_months = FusiCode.fusi.filter(TimeStamp__year=año_actual) \
    .annotate(month=F('TimeStamp__month')) \
    .values('month') \
    .annotate(total_registros=Count('id')) \
    .order_by('month')

    #------------------------------------------------------------------------------

    open_fusi = FusiCode.fusi.all().exclude(fusi_state='Cerrado')
    open_fusi = open_fusi.exclude(fusi_code__in=filter_fusi_code)
    open_fusi = open_fusi.order_by('-TimeStamp')
    open_fusi = open_fusi.filter(TimeStamp__year=año_actual, TimeStamp__month=mes_actual)
    page = request.GET.get('page')
    results = 100
    paginator = Paginator(open_fusi, results)
    try:
        open_fusi = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        open_fusi = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        open_fusi = paginator.page(page)
    #-----------------------------------------------------------------------------------------
    messages = FusiMessage.fusi.all()

    for code in open_fusi:
        for fusi_message in messages:
            if code.fusi_code == fusi_message.fusi_code:
                code.fusi_description = fusi_message.fusi_description
                break
    #-----------------------------------------------------------------------------------------
    buses_name = Bus.bus.values('bus_name', 'id')
    top_ten_code_selected_bus = None
    selected_bus = None 
    selected_bus_name = None
    recurrent_code = None
    labels_top_ten = None
    labels_top_ten
    if request.method == "POST":
        selected_bus = request.POST.get('bus_id')
        bus = Bus.bus.filter(id=selected_bus).first()
        if bus:
          selected_bus_name = bus.bus_name
    selected_bus_code_count = FusiCode.fusi.filter(bus=selected_bus).count()
    recurrent_code = (
    FusiCode.fusi.filter(bus=selected_bus)
    .values('fusi_code')  
    .annotate(code_count=Count('fusi_code'))  
    .order_by('-code_count')  
    .first()  
    )
    top_ten_code_selected_bus = (FusiCode.fusi.filter(bus=selected_bus)
                                 .values('fusi_code')
                                 .annotate(code_count=Count('fusi_code'))
                                 .order_by('-code_count'))[:10]
    labels_top_ten = [item['fusi_code'] for item in top_ten_code_selected_bus]
    data_top_ten = [item['code_count'] for item in top_ten_code_selected_bus]
    selected_bus_fusi = FusiCode.fusi.filter(TimeStamp__year=año_actual, TimeStamp__month=mes_actual, bus=selected_bus)
    #-----------------------------------------------------------------------------------------
    codes = FusiMessage.fusi.values_list('fusi_code', flat=True)
    #-----------------------------------------------------------------------------------------

    context = {
        'selected_bus_fusi':selected_bus_fusi,
        'labels_top_ten':labels_top_ten,
        'data_top_ten': data_top_ten,
        'top_ten_code_selected_bus':top_ten_code_selected_bus,
        'recurrent_code':recurrent_code,
        'selected_bus_name':selected_bus_name,
        'selected_bus_code_count':selected_bus_code_count,
        'codes':codes,
        'active_fusi': open_fusi,
        'buses_name': buses_name,
        'paginator': paginator,
        'total_fusi': total_fusi,
        'cant_fusi_month':  cant_fusi_month,
        'nombre_mes': nombre_mes,
        'baddest_bus_name': baddest_bus_name,
        'total_baddest_bus_reg': total_badddest_bus_reg,
        'worst_year': worst_year, 
        'worst_month_reg': worst_month_reg,  
        'total_reg_worst': total_reg_worst,  
        'worst_month_name':worst_month_name,
         'worst_year': worst_year,
         'fusi_months': fusi_months,
         'meses_es': meses_es,
         'message':messages,

        }
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
    now = timezone.now()
    año = now.year
    mes = now.month
    results = daily_bus_km(pk, año)
    results.sort(key=lambda x: x[0])
    
    montly_result = monthly_bus_km(pk)

# Tabla recorrido buses
    result_data = get_monthly_kilometer_data(pk, año)
    ot = WorkOrder.objects.filter(bus=pk)
    bus = Bus.bus.get(pk=pk)

    soh = 0
    try:
     latest_battery_health = BatteryHealth.battery_health.filter(bus_id=pk).latest('battery_health_value')
     soh = latest_battery_health
    except ObjectDoesNotExist:
     print('No se encontraron registros en BatteryHealth para el bus_id especificado.')

    fusi_codes = FusiCode.fusi.filter(
    bus_id=pk,
    TimeStamp__year=año,
    TimeStamp__month=mes
    ).order_by('-TimeStamp')[:600]

    messages = FusiMessage.fusi.all()

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
    #month_name_to_number = {
    #'Enero': '01',
    #'Febrero': '02',
    #'Marzo': '03',
    #'Abril': '04',
    #'Mayo': '05',
    #'Junio': '06',
    #'Julio': '07',
    #'Agosto': '08',
    #'Septiembre': '09',
    #'Octubre': '10',
    #'Noviembre': '11',
    #'Diciembre': '12'
#}
    #combined_data = []
    #calc_rendimiento = lambda energy, diff: round(float(energy) / float(diff), 2) if diff and energy and isinstance(diff, (int, float)) and isinstance(energy, (int, float)) else None


    #for item in result_data:
        #month_name = item['month']
        #month_number = month_name_to_number[month_name]
        #energy = float(monthly_totals_dict.get(month_number, 0))
    
        #difference = item['difference']
        #if isinstance(difference, str) or difference == 0:
         #   difference = None  # O manejar de otra forma, dependiendo de la lógica de negocio

        #combined_data.append({
         #   'month': month_name,
          #  'difference': difference,
           # 'energy': energy,
            #'rendimiento': calc_rendimiento(energy, difference)
        #})

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
               #'rendimiento': combined_data,
                
                }
    return render(request, 'bus/bus-profile.html', context_perfil)


@login_required(login_url='login')
def dashboard(request):
    #-----------------------------------------------------------------------------
    # API Link
    data = fs_link_api()
    cant_fs = (data['cant_fs'])
    fs_vehicles = data['data']
    
    #-----------------------------------------------------------------------------------------------------------
    # cantidad de buses en la flota
    #optimizada
    total_flota = total_flota = Bus.bus.filter(~Q(id__in=no_update_list)).aggregate(total=Count('id'))['total']
     # buses en Operacion
    operacion = total_flota - cant_fs
    #---------------------------------------------------------------------------------------------
    # datos tabla de buses
    # optimizada
    complete_table = Bus.bus.exclude(lts_update=None).order_by('-lts_update').values(
        'id','bus_name','lts_soc','lts_odometer','lts_isolation','lts_24_volt','lts_fusi',
        'charging','lts_update','key_state','ecu_state','bus_series')
    #------------------------------------------------------------------------------------------------
    # buses cargando
    charging = Bus.bus.filter(charging=1).count()
   
    # paginador tabla
    page = request.GET.get('page', 1)
    results = 7
    paginator = Paginator(complete_table, results)
    try:
        complete_table = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        complete_table = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        complete_table = paginator.page(page)
    #-----------------------------------------------------------------------------------------------

    # km total de la flota
    # optimizado
    km_total = Bus.bus.annotate(max_odometer=Max
                                ('odometer__odometer_value')).aggregate(
                                    total_km=Sum('max_odometer'))['total_km'] or 0  
    
#-----------------------------------------------------------------------------------------------------
    #co2 ahorrado total flota
    #optimizada
  
    co2_total = round(km_total * 0.00067, 2)

#-------------------------------------------------------------------------------------------------------

    # menor 50 optimizada
    # cantidad de buses con soc menor a 50
    cant_low_50_soc = Bus.bus.filter(lts_soc__lt=50).exclude(lts_soc=0.0).count()

#------------------------------------------------------------------------------------------------------    
    # cantidad buses con cola de archivos
    #optimizada
    bus_instance = Bus()
    delayed = bus_instance.delay_data().exclude(id__in=no_update_list).count()


# -------------------------------------------------------------------------------------------------------
   
    energia_anual = AnualEnergy.objects.first()
    energia_anual = energia_anual.energia
    request.session['energia_anual'] = energia_anual
    request.session['km_total'] = km_total
    request.session['cant_low_50_soc'] = cant_low_50_soc 
    request.session['delay'] = delayed
    
#---------------------------------------------------------------------------------------------------------
    request.session['charging'] = charging
    request.session['cant_fs']= cant_fs
    request.session['total_flota'] = total_flota
    request.session['operacion'] = operacion
#---------------------------------------------------------------------------------------------------------
 
    
#----------------------------------------------------------------------------------------------------------
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



    context = {
       
        'operacion': operacion,
        'km_total': km_total,
        'total_flota': total_flota,
        'bus': complete_table,
        'cant_low_50_soc': cant_low_50_soc,
        'delayed': delayed,
        'paginator': paginator,
        'cant_fs': cant_fs,
        'co2_total': co2_total,
       # 'fusi_grafico': fusi_grafico,
        #'linechart_data': linechart_data,
        #'linechart_data2': linechart_data2,
        'charging': charging,
        'fs_vehicles': fs_vehicles,
        'energia_anual':energia_anual,
    }
    return render(request, 'pages/dashboard.html', context)


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


def energy_record(request):

    #----------buses cargando----------------------------------
 charging = request.session.get('charging')
 energia_anual = request.session.get('energia_anual')
    #---------------------------------------------------------
   
 bus_id = 40  # Cambia por el ID del bus que deseas filtrar
 mes = 8    # Cambia por el mes que deseas (número de mes)

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