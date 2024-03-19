from django.shortcuts import render, redirect
from .models import Bus, FusiMessage, Odometer, FusiCode
from .forms import BusForm, FusiMessageForm, FusiForm
from users.models import WorkOrder
from .query_utils import daily_bus_km, monthly_bus_km, monthly_fleet_km
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
# pdf imports 
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from django.http import FileResponse
from reportlab.lib.pagesizes import letter, landscape
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
import xlwt
# manejo errores paginador
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone


filter_fusi_code = [21004.0, 20507.0, 20503.0, 20511.0, 20509.0, 20498.0, 20506.0, 20525.0, 16911.0, 20519.0, 20499.0, 20505.0,
20502.0, 21777.0, 21780.0, 20500.0, 20508.0, 20510.0, 20504.0, 20520.0, 20515.0, 20501.0]

no_update_list = ['27','34', '60', '24', '87', '116', '21', '61', '82', '83', '81']



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
    
    no_update = Bus.bus.filter(lts_update=None)
    
    no_update = no_update.exclude(id__in=no_update_list)

    low_battery = Bus.bus.filter(lts_24_volt__lt=20)
    low_battery = low_battery.exclude(lts_24_volt=0.0)

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

    context = {
        'list_fs_bus': list_fs_bus,
        'low_battery': low_battery,
        'no_update': no_update,
        'delayed': delayed,
        'low_50_soc_count': low_50_soc_count,
        'paginator_no_update': paginator_no_update,
        'paginator_delayed': paginator_delayed
    }
    return render(request, 'pages/warnings.html', context)


@login_required(login_url='login')
def reports_page(request):
    return render(request, 'reports/reports.html')


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
    # fusicodes monthly
    current_month = timezone.now().month
    distinct_fusi_code = FusiCode.fusi.filter(TimeStamp__month=current_month).values('fusi_code').annotate(total=Count('fusi_code')).order_by('-total')
    distinct_fusi_code = distinct_fusi_code.exclude(fusi_code__in=filter_fusi_code)
    current_datetime = timezone.now()
    mes_actual = current_datetime.strftime('%B')
  
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

# top 10 buses fusi code
    top_buses = FusiCode.fusi.values('bus__bus_name').annotate(num_registros=Count('bus')).order_by('-num_registros')[:10]


    context = {
        'mes_actual': mes_actual,
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
        'paginator_fusi': paginator_fusi,
        'distinct_fusi_code': distinct_fusi_code,
        'top_buses': top_buses,
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
        ('BACKGROUND', (0, 0), (-1, 0), 'grey'),
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
    image_width = 200
    image_height = 200
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


def pdf_report(request):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte dia :{formatted_datetime}.pdf'
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    elements = []

    table_data = [
        ["Bus Name", "Sniffer", "LTS SOC", "LTS Odometer", "LTS Update"]
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
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'user successfully logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'username or password incorrect')
            print('Username or password is incorrect')

    return render(request, 'pages/login.html')


def logout_user(request):
    logout(request)
    messages.error(request, 'user successfully logged out')

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
    ot = WorkOrder.objects.filter(bus=pk)
    bus = Bus.bus.get(pk=pk)
    fusi = FusiCode.fusi.filter(bus_id=pk)
    context = {'bus': bus, 'ot': ot, 'results': results, 'monthly_result': montly_result, 'fusi': fusi}
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



