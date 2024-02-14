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
from django.db.models import Q
from django.db.models import Sum

# pdf imports 
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from django.http import FileResponse
from reportlab.lib.pagesizes import letter, landscape
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
import xlwt

@login_required(login_url='login')
def reports_page(request):
    return render(request, 'bus_signals/reports.html')


@login_required(login_url='login')
def dashboard(request):
    active_fusi3 = FusiCode.fusi.all().exclude(fusi_state='Cerrado')
    active_fusi2 = active_fusi3.count()
    total_flota = Bus.bus.count()
    complete_table = Bus.bus.all()
    complete_table = complete_table.exclude(lts_update=None)
    low_50_soc_records = Bus.bus.filter(lts_soc__lt=65)
    active_fusi = FusiCode.fusi.all()
    km_total = Bus.bus.aggregate(Sum('lts_odometer'))['lts_odometer__sum'] or 0
    km_total_format = '{:,.0f}'.format(km_total)
    km_total_format = km_total_format.replace(',', '.')
    low_50_soc_count = low_50_soc_records.all().exclude(lts_soc=0.0)
    low_battery = Bus.bus.filter(lts_24_volt__lt=20)
    low_battery = low_battery.exclude(lts_24_volt=0.0)
    
    context = {
        'km_total': km_total_format,
        'low_50_soc_count': low_50_soc_count,
        'active_fusi': active_fusi, 
        'total_flota': total_flota,
        'low_battery': low_battery,
        'active_fusi2': active_fusi2,
        'complete_table': complete_table,
        }
    return render(request, 'bus_signals/dashboard.html', context)

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
        row = [bus.bus_name, bus.sniffer, str(bus.lts_soc), str(bus.lts_odometer)+ 'km', formatted_datetime]
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
        row = [bus.bus_name, bus.sniffer, str(bus.lts_soc), str(bus.lts_odometer)+ 'km', formatted_datetime]
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

    return render(request, 'login.html')

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
def update_fusicode(request, pk):
    fusi_code = FusiCode.fusi.get(id=pk)
    form = FusiForm(instance=fusi_code)
    if request.method =='POST':
        form = FusiForm(request.POST, instance=fusi_code)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'bus_signals/fusicode_form.html', context)

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
    fusi = FusiCode.fusi.filter(bus_id=pk)
    context = {'bus': bus, 'ot': ot, 'results': results, 'monthly_result': montly_result, 'fusi': fusi}
    return render(request, 'bus_signals/bus_detail.html', context)

@login_required(login_url='login')
def bus_list(request):
    search_query = ''
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
    buses = Bus.bus.filter(
        Q(bus_name__icontains=search_query) |
        Q(bus_series__icontains=search_query) |
        Q(bus_ecu__icontains=search_query) |
        Q(client__icontains=search_query) 
        )
    context = {'bus': buses, 'search_query': search_query}
    return render(request, 'bus_signals/bus_list.html', context)

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
    context = {'fusi': messages, 'search_query': search_query}
    return render(request, 'bus_signals/dic_fusi.html', context)

@login_required(login_url='login')
def odometer(request):
    return render(request, 'bus_signals/odometer.html')
