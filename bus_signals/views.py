from django.shortcuts import render, redirect
from .models import Bus, FusiMessage, Odometer, FusiCode
from users.models import WorkOrder
from .forms import BusForm, FusiMessageForm, FusiForm
from .query_utils import daily_bus_km, monthly_bus_km, monthly_fleet_km
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
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
from django.utils import timezone


filter_fusi_code = [21004.0, 20507.0, 20503.0, 20511.0, 20509.0, 20498.0, 20506.0, 20525.0, 16911.0, 20519.0, 20499.0, 20505.0,
20502.0, 21777.0, 21780.0, 20500.0, 20508.0, 20510.0, 20504.0, 20520.0, 20515.0, 20501.0]

no_update_list = ['27','34', '60', '24', '87', '116', '21', '61', '82', '83', '81']

def no_access(request):
    return render(request, 'pages/no-access.html')
@login_required(login_url='login')
def warnings(request):
    headers = {
    'User-Agent': 'Alicanto/1.0',
}
    api_url = 'https://reborn.assay.cl/api/v1/fs_elec'
    response = requests.get(api_url, headers=headers)
    data = response.json()
    list_fs_bus = data['data']
    bus_instance = Bus()
    delayed = bus_instance.delay_data()
    low_50_soc_records = Bus.bus.filter(lts_soc__lt=50)
    low_50_soc_count = low_50_soc_records.all().exclude(lts_soc=0.0)

    top_buses = FusiCode.fusi.values('bus__bus_name').annotate(num_registros=Count('bus')).order_by('-num_registros')[:10]
    
    no_update = Bus.bus.filter(lts_update=None)
    
    no_update = no_update.exclude(id__in=no_update_list)

    low_battery = Bus.bus.filter(lts_24_volt__lt=20)
    low_battery = low_battery.exclude(lts_24_volt=0.0)


     # fusicodes monthly
    current_month = timezone.now().month
    distinct_fusi_code = FusiCode.fusi.filter(TimeStamp__month=current_month).values('fusi_code').annotate(total=Count('fusi_code')).order_by('-total')
    distinct_fusi_code = distinct_fusi_code.exclude(fusi_code__in=filter_fusi_code)
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
    results_fusi = 12
    paginator_fusi = Paginator(distinct_fusi_code, results_fusi)
    try:
        distinct_fusi_code = paginator_fusi.page(page_fusi)
    except PageNotAnInteger:
        page_fusi = 1
        distinct_fusi_code = paginator_fusi.page(page_fusi)
    except EmptyPage:
        page_fusi = paginator_fusi.num_pages
        distinct_fusi_code = paginator_fusi.page(page_fusi)


    context = {
         'mes_actual': mes_actual,
        'list_fs_bus': list_fs_bus,
        'low_battery': low_battery,
        'no_update': no_update,
        'delayed': delayed,
        'low_50_soc_count': low_50_soc_count,
        'paginator_no_update': paginator_no_update,
        'paginator_delayed': paginator_delayed,
        'top_buses': top_buses,
        'distinct_fusi_code': distinct_fusi_code,
          'paginator_fusi': paginator_fusi,
    }
    return render(request, 'pages/warnings.html', context)


@login_required(login_url='login')
def reports_page(request):
    bus = Bus.bus.all()

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
def dashboard(request):
    headers = {
    'User-Agent': 'Alicanto/1.0',
}
    api_url = 'https://reborn.assay.cl/api/v1/fs_elec'
    response = requests.get(api_url, headers=headers)
    data = response.json()
    cant_fs = len(data['data'])
   
  
    # cantidad de fusi abiertos
    open_fusi = FusiCode.fusi.all().exclude(fusi_state='Cerrado').count()
    # cantidad de buses en la flota
    total_flota = Bus.bus.exclude(id__in=no_update_list)
    total_flota = total_flota.count()
    
    # datos tabla de buses
    complete_table = Bus.bus.all()
    complete_table = complete_table.exclude(lts_update=None)
    complete_table = complete_table.order_by('-lts_update')
    # km total de la flota
    km_total = Bus.bus.aggregate(Sum('lts_odometer'))['lts_odometer__sum'] or 0
    km_total_format = '{:,.0f}'.format(km_total)
    km_total_format = km_total_format.replace(',', '.')

    low_50_soc_records = Bus.bus.filter(lts_soc__lt=50)
    low_50_soc_count = low_50_soc_records.all().exclude(lts_soc=0.0)
    # cantidad de buses sin actualizacion
    no_update = Bus.bus.filter(lts_update=None)
    no_update = no_update.exclude(id__in=no_update_list).count()
    # cantidad de buses con soc menor a 50
    cant_low_50_soc = low_50_soc_count.count()
    # cantidad buses con cola de archivos
    bus_instance = Bus()
    delayed = bus_instance.delay_data().count()

    operacion = total_flota - cant_fs

    page = request.GET.get('page', 1)
    results = 10
    paginator = Paginator(complete_table, results)
    try:
        complete_table = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        complete_table = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        complete_table = paginator.page(page)



    context = {
       
        'operacion': operacion,
        'km_total': km_total_format,
        'low_50_soc_count': low_50_soc_count,
        'total_flota': total_flota,
        'bus': complete_table,
        'no_update': no_update,
        'cant_low_50_soc': cant_low_50_soc,
        'open_fusi': open_fusi,
        'delayed': delayed,
        'paginator': paginator,
        'cant_fs': cant_fs,
    }
    return render(request, 'pages/dashboard.html', context)



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


def monthly_bus_report(request):
    report_data = monthly_fleet_km()
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte km mensual :{formatted_datetime}.pdf'
    buf = io.BytesIO()

    doc = SimpleDocTemplate(buf, pagesize=landscape(letter))
    elements = []

    table_data = [
        [
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


def xls_report(request):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte dia :{formatted_datetime}.xls'
    buf = io.BytesIO()

    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('Report')

    table_data = [
        ["Bus Name", "Sniffer", "LTS SOC", "LTS Odometer", "LTS Update"]
    ]

    bus_list = Bus.bus.all()
    for bus in bus_list:
        formatted_datetime = bus.lts_update.strftime("%d/%m/%Y %H:%M") if bus.lts_update else "sin actualizacion"
        row = [bus.bus_name, bus.sniffer, str(bus.lts_soc), str(bus.lts_odometer) + 'km', formatted_datetime]
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
    

@login_required(login_url='login')
def daily_bus_km_report_pdf(request, pk):
    bus = Bus.bus.get(id=pk)
    result = daily_bus_km(pk)

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'km_diario_bus_{bus.bus_name}_{formatted_datetime}.pdf'
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    elements = []

    table_data = [
        ["Dia", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    ]

    # Crear una lista de listas con los datos de result organizados por mes
    data_by_month = [[] for _ in range(12)]  # 12 meses
    for item in result:
        for idx, value in enumerate(item[1:], start=1):
            if value is not None:
                data_by_month[idx - 1].append(value)
            else:
                data_by_month[idx - 1].append('')

    # Llenar la tabla con los datos organizados
    for i in range(31):  # 31 días
        row = [f"Día {i+1}"]
        for month_data in data_by_month:
            if i < len(month_data):
                row.append(month_data[i])
            else:
                row.append('')
        table_data.append(row)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), 'grey'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), 'lightgrey'),
        ('LINEBELOW', (0, 1), (-1, -1), 1, 'black')
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
            messages.success(request, 'Ingresaste coreectamente')
            return redirect('dashboard')
        else:
            messages.error(request, 'nombre de usuario o contraseña incorrectos')
           

    return render(request, 'pages/login.html')


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

    # Iterar sobre el rango correcto para cada mes
    for i in range(1, len(montly_result[0]), 2):
        if i + 1 < len(montly_result[0]) and montly_result[0][i] is not None and montly_result[0][i + 1] is not None:
            difference = montly_result[0][i + 1] - montly_result[0][i]
            month_name = months_dict[(i + 1) // 2]  # Obtener el nombre del mes del diccionario
            result_data.append({
                'month': month_name,
                'value1': montly_result[0][i],
                'value2': montly_result[0][i + 1],
                'difference': difference if difference is not None else 'N/A'
            })
    
    ot = WorkOrder.objects.filter(bus=pk)
    bus = Bus.bus.get(pk=pk)
    co2 = (bus.lts_odometer / 0.2857) * 2.68
   
    co2 = co2/1000
    co2 = round(co2, 2)
    print(co2)
    fusi = FusiCode.fusi.filter(bus_id=pk).order_by('-TimeStamp')
    context = {'bus': bus, 'ot': ot, 'results': results, 'monthly_result': montly_result, 'fusi': fusi, 'result_data': result_data, 'co2': co2}
    return render(request, 'bus/bus-profile.html', context)


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



