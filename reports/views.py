from django.shortcuts import render, redirect
from openpyxl import Workbook
from bus_signals.query_utils import matriz_km_diario_flota, format_date, daily_bus_km, monthly_bus_km
from bus_signals.models import Bus, BatteryHealth, ChargeStatus, CellsVoltage, EcuState
from . models import Prueba, DisponibilidadFlota
from datetime import date, timedelta, timezone
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import io
from reportlab.platypus import Spacer
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.http import FileResponse, HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
import xlwt
from io import BytesIO
import psycopg2
from django.contrib import messages
from django.db.models import Max
from datetime import datetime
from django.utils import timezone
import requests
from django.contrib.auth.decorators import login_required
import pytz
no_update_list = ['24', '87', '61','87', '137', '132', '134', '133', '130', '129', '128', '131', '136', '135' ]

#funcion reporte matriz seleccionando mes y año
@login_required(login_url='login')
def historical_data(request):
     if request.method == 'GET':
        context = {
            'bus': Bus.bus.all().exclude(id__in=no_update_list),
            'meses2': [{'mes':'Enero', 'numero':1}, {'mes':'Febrero', 'numero':2},{'mes':'Marzo', 'numero':3}, {'mes':'Abril', 'numero':4},
                       {'mes':'Mayo', 'numero':5}, {'mes':'Junio', 'numero':6}, {'mes':'Julio', 'numero':7}, {'mes':'Agosto', 'numero':8},
                       {'mes':'Septiembre', 'numero':9}, {'mes':'Octubre', 'numero':10}, {'mes':'Noviembre', 'numero':11}, {'mes':'Diciembre', 'numero':12}],
        }
      
        # Lógica para manejar la solicitud GET
        return render(request, 'reports/historicos.html', context)
     
     if request.method == 'POST':
        current_datetime = datetime.now()
        dbname = 'alicanto-db-dev'
        user = 'postgres'
        password = 'postgres'
        host = 'alicanto-db-v1.cyydo36bjzsy.us-west-1.rds.amazonaws.com'
        port = '5432'
        mes = request.POST['mes']
        año = request.POST['año']
        bus = Bus.bus.only('id', 'bus_name')
        bus = bus.exclude(id__in=no_update_list)
        table_data = [
            ["Mes", "Bus", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
             "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27",
             "28", "29", "30", "31"]
        ]
        
        formatted_datetime = current_datetime.strftime("%d-%m-%Y")
        filename = f'matriz km diario flota historico mes:{mes}-{año}.xls'
        buf = io.BytesIO()
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Report')

        # Escribir encabezados
        for col_index, header in enumerate(table_data[0]):
            worksheet.write(0, col_index, header)

        row_index = 1  # Comenzar desde la segunda fila

        # Procesar cada autobús
        for i in bus:
            bus_id = i.id
            name = i.bus_name
            connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
            cursor = connection.cursor()
            query = """SELECT
      CASE mes
        WHEN 1 THEN 'Enero'
        WHEN 2 THEN 'Febrero'
        WHEN 3 THEN 'Marzo'
        WHEN 4 THEN 'Abril'
        WHEN 5 THEN 'Mayo'
        WHEN 6 THEN 'Junio'
        WHEN 7 THEN 'Julio'
        WHEN 8 THEN 'Agosto'
        WHEN 9 THEN 'Septiembre'
        WHEN 10 THEN 'Octubre'
        WHEN 11 THEN 'Noviembre'
        WHEN 12 THEN 'Diciembre'
      END AS mes,
      bus_signals_bus.bus_name AS bus,
      MAX(CASE WHEN dia = 1 THEN max_odometer END) AS "1",
      MAX(CASE WHEN dia = 2 THEN max_odometer END) AS "2",
      MAX(CASE WHEN dia = 3 THEN max_odometer END) AS "3",
      MAX(CASE WHEN dia = 4 THEN max_odometer END) AS "4",
      MAX(CASE WHEN dia = 5 THEN max_odometer END) AS "5",
      MAX(CASE WHEN dia = 6 THEN max_odometer END) AS "6",
      MAX(CASE WHEN dia = 7 THEN max_odometer END) AS "7",
      MAX(CASE WHEN dia = 8 THEN max_odometer END) AS "8",
      MAX(CASE WHEN dia = 9 THEN max_odometer END) AS "9",
      MAX(CASE WHEN dia = 10 THEN max_odometer END) AS "10",
      MAX(CASE WHEN dia = 11 THEN max_odometer END) AS "11",
      MAX(CASE WHEN dia = 12 THEN max_odometer END) AS "12",
      MAX(CASE WHEN dia = 13 THEN max_odometer END) AS "13",
      MAX(CASE WHEN dia = 14 THEN max_odometer END) AS "14",
      MAX(CASE WHEN dia = 15 THEN max_odometer END) AS "15",
      MAX(CASE WHEN dia = 16 THEN max_odometer END) AS "16",
      MAX(CASE WHEN dia = 17 THEN max_odometer END) AS "17",
      MAX(CASE WHEN dia = 18 THEN max_odometer END) AS "18",
      MAX(CASE WHEN dia = 19 THEN max_odometer END) AS "19",
      MAX(CASE WHEN dia = 20 THEN max_odometer END) AS "20",
      MAX(CASE WHEN dia = 21 THEN max_odometer END) AS "21",
      MAX(CASE WHEN dia = 22 THEN max_odometer END) AS "22",
      MAX(CASE WHEN dia = 23 THEN max_odometer END) AS "23",
      MAX(CASE WHEN dia = 24 THEN max_odometer END) AS "24",
      MAX(CASE WHEN dia = 25 THEN max_odometer END) AS "25",
      MAX(CASE WHEN dia = 26 THEN max_odometer END) AS "26",
      MAX(CASE WHEN dia = 27 THEN max_odometer END) AS "27",
      MAX(CASE WHEN dia = 28 THEN max_odometer END) AS "28",
      MAX(CASE WHEN dia = 29 THEN max_odometer END) AS "29",
      MAX(CASE WHEN dia = 30 THEN max_odometer END) AS "30",
      MAX(CASE WHEN dia = 31 THEN max_odometer END) AS "31"
      FROM (
         SELECT
            EXTRACT(MONTH FROM "TimeStamp") AS mes,
            EXTRACT(DAY FROM "TimeStamp") AS dia,
            EXTRACT(YEAR FROM "TimeStamp") AS año,
            MAX(odometer_value) AS max_odometer,
            bus_id
      FROM
        bus_signals_odometer

      GROUP BY
        EXTRACT(MONTH FROM "TimeStamp"),
        EXTRACT(DAY FROM "TimeStamp"),
        EXTRACT(YEAR FROM "TimeStamp"),
        bus_id
               ) AS max_odometers
      LEFT JOIN bus_signals_bus ON max_odometers.bus_id = bus_signals_bus.id
      WHERE
         bus_id = %s
         AND mes = %s
         AND año = %s
         GROUP BY
         mes, bus, año;"""
            cursor.execute(query, (bus_id, mes, año))
            results = cursor.fetchall()

            if results and len(results[0]) >= 32:
                row = [results[0][0], results[0][1]]  # Agrega el mes y el bus al principio
                row.extend([value if value is not None else 0 for value in results[0][2:]])  # Agrega los valores de los días
                table_data.append(row)
            else:
                row = [mes, name, 0]  # Agrega el mes, el bus y un valor predeterminado
                table_data.append(row)

            cursor.close()
            connection.close()

        # Escribir datos en la hoja de cálculo
        for row_data in table_data:
            for col_index, cell_data in enumerate(row_data):
                worksheet.write(row_index, col_index, cell_data)
            row_index += 1

        # Guardar el archivo Excel en el buffer
        workbook.save(buf)
        buf.seek(0)

        return FileResponse(buf, as_attachment=True, filename=filename)
     
def historic_bus_report(request):
   if request.method == 'GET':
        # Lógica para manejar la solicitud GET
        return render(request, 'reports/historicos.html')
   if request.method == 'POST':
        current_datetime = datetime.now()
        dbname = 'alicanto-db-dev'
        user = 'postgres'
        password = 'postgres'
        host = 'alicanto-db-v1.cyydo36bjzsy.us-west-1.rds.amazonaws.com'
        port = '5432'
        mes = request.POST['mes']
        año = request.POST['año']
        bus = request.POST['bus']
        for i in Bus.bus.all():
            if bus == i.id:
                name = i.bus_name
                break
        table_data = [
            ["Mes", "Bus", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
             "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27",
             "28", "29", "30", "31"]
        ]
        filename = f'km diario bus id:{bus}-mes:{mes}-año:{año}.xls'
        buf = io.BytesIO()
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Report')
        for col_index, header in enumerate(table_data[0]):
            worksheet.write(0, col_index, header)

        row_index = 1  # Comenzar desde la segunda fila
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = connection.cursor()
        query = """SELECT
        CASE mes
        WHEN 1 THEN 'Enero'
        WHEN 2 THEN 'Febrero'
        WHEN 3 THEN 'Marzo'
        WHEN 4 THEN 'Abril'
        WHEN 5 THEN 'Mayo'
        WHEN 6 THEN 'Junio'
        WHEN 7 THEN 'Julio'
        WHEN 8 THEN 'Agosto'
        WHEN 9 THEN 'Septiembre'
        WHEN 10 THEN 'Octubre'
        WHEN 11 THEN 'Noviembre'
        WHEN 12 THEN 'Diciembre'
        END AS mes,
        bus_signals_bus.bus_name AS bus,
        MAX(CASE WHEN dia = 1 THEN max_odometer END) AS "1",
        MAX(CASE WHEN dia = 2 THEN max_odometer END) AS "2",
        MAX(CASE WHEN dia = 3 THEN max_odometer END) AS "3",
        MAX(CASE WHEN dia = 4 THEN max_odometer END) AS "4",
        MAX(CASE WHEN dia = 5 THEN max_odometer END) AS "5",
        MAX(CASE WHEN dia = 6 THEN max_odometer END) AS "6",
        MAX(CASE WHEN dia = 7 THEN max_odometer END) AS "7",
        MAX(CASE WHEN dia = 8 THEN max_odometer END) AS "8",
        MAX(CASE WHEN dia = 9 THEN max_odometer END) AS "9",
        MAX(CASE WHEN dia = 10 THEN max_odometer END) AS "10",
        MAX(CASE WHEN dia = 11 THEN max_odometer END) AS "11",
        MAX(CASE WHEN dia = 12 THEN max_odometer END) AS "12",
        MAX(CASE WHEN dia = 13 THEN max_odometer END) AS "13",
        MAX(CASE WHEN dia = 14 THEN max_odometer END) AS "14",
        MAX(CASE WHEN dia = 15 THEN max_odometer END) AS "15",
        MAX(CASE WHEN dia = 16 THEN max_odometer END) AS "16",
        MAX(CASE WHEN dia = 17 THEN max_odometer END) AS "17",
        MAX(CASE WHEN dia = 18 THEN max_odometer END) AS "18",
        MAX(CASE WHEN dia = 19 THEN max_odometer END) AS "19",
        MAX(CASE WHEN dia = 20 THEN max_odometer END) AS "20",
        MAX(CASE WHEN dia = 21 THEN max_odometer END) AS "21",
        MAX(CASE WHEN dia = 22 THEN max_odometer END) AS "22",
        MAX(CASE WHEN dia = 23 THEN max_odometer END) AS "23",
        MAX(CASE WHEN dia = 24 THEN max_odometer END) AS "24",
        MAX(CASE WHEN dia = 25 THEN max_odometer END) AS "25",
        MAX(CASE WHEN dia = 26 THEN max_odometer END) AS "26",
        MAX(CASE WHEN dia = 27 THEN max_odometer END) AS "27",
        MAX(CASE WHEN dia = 28 THEN max_odometer END) AS "28",
        MAX(CASE WHEN dia = 29 THEN max_odometer END) AS "29",
        MAX(CASE WHEN dia = 30 THEN max_odometer END) AS "30",
        MAX(CASE WHEN dia = 31 THEN max_odometer END) AS "31"
        FROM (
        SELECT
        EXTRACT(MONTH FROM "TimeStamp") AS mes,
        EXTRACT(DAY FROM "TimeStamp") AS dia,
        EXTRACT(YEAR FROM "TimeStamp") AS año,
        MAX(odometer_value) AS max_odometer,
        bus_id
        FROM
        bus_signals_odometer

        GROUP BY
        EXTRACT(MONTH FROM "TimeStamp"),
        EXTRACT(DAY FROM "TimeStamp"),
        EXTRACT(YEAR FROM "TimeStamp"),
        bus_id
               ) AS max_odometers
        LEFT JOIN bus_signals_bus ON max_odometers.bus_id = bus_signals_bus.id
        WHERE
        bus_id = %s
        AND mes = %s
        AND año = %s
        GROUP BY
        mes, bus, año;"""
        cursor.execute(query, (bus, mes, año))
        results = cursor.fetchall()
        if results and len(results[0]) >= 32:
            row = [results[0][0], results[0][1]]  # Agrega el mes y el bus al principio
            row.extend([value if value is not None else 0 for value in results[0][2:]])  # Agrega los valores de los días
            table_data.append(row)
        else:
            row = [mes, name, 0]  # Agrega el mes, el bus y un valor predeterminado
            table_data.append(row)
        cursor.close()
        connection.close()

        for row_data in table_data:
            for col_index, cell_data in enumerate(row_data):
                worksheet.write(row_index, col_index, cell_data)
            row_index += 1
        workbook.save(buf)
        buf.seek(0)

        return FileResponse(buf, as_attachment=True, filename=filename)
        

@login_required(login_url='login')
def dashboard_disponibilidad_flota(request):
   headers = { 'User-Agent': 'Alicanto/1.0', }
   api_url = 'https://reborn.assay.cl/api/v1/fs_elec'
   response = requests.get(api_url, headers=headers)
   data = response.json()
   list_fs_bus = data['data']
   cant_fs = len(data['data'])
   total_flota = Bus.bus.exclude(id__in=no_update_list)
   total_flota = total_flota.count()
   operacion = total_flota - cant_fs
   context = {
      'fs': list_fs_bus,
      'cant_fs': cant_fs,
      'total_flota': total_flota,
      'operacion': operacion,
   }
   return render(request, 'reports/disponibilidad_flota.html', context)

@login_required(login_url='login')
def disponbilidad_flota(request):
   headers = { 'User-Agent': 'Alicanto/1.0', }
   api_url = 'https://reborn.assay.cl/api/v1/fs_elec'
   response = requests.get(api_url, headers=headers)
   data = response.json()
   bus_fs = []
   for i in data['data']:
      bus_fs.append(i['vehicle'].capitalize())
   bus_operativo = Bus.bus.all().exclude(bus_name__in=bus_fs)
   bus_operativo = bus_operativo.exclude(id__in=no_update_list)
   
   for bus in bus_operativo:
    disponibilidad_flota1 = DisponibilidadFlota(
        bus=str(bus.bus_name),
        serie=str(bus.bus_series),
        disponibilidad=True,
        dias_operativos=1,
        dias_fs=0,
    )
    disponibilidad_flota1.save()
  

   for bus in bus_fs:
      disponibilidad_flota = DisponibilidadFlota(
         bus=str(bus),
         disponibilidad=False,
         dias_operativos=0,
         dias_fs=1,
      )
      disponibilidad_flota.save()

   

   

   
   messages.success(request, 'Los registros se actualizaron correctamente.')
   return redirect('disponibilidad-flota')


@login_required(login_url='login')
def energy_report(request):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    filename = f'reporte_energia_flota_{formatted_datetime}.xls'
    buf = io.BytesIO()
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('Report')

    # Inicializamos table_data con las cabeceras
    table_data = [["Bus"] + [str(day) for day in range(1, 32)]]

    energia_cargada_flota = 0
    lista_datos_organizados = []
    for y in Bus.bus.all().exclude(id__in=no_update_list):
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
        if rango_actual:
            rangos.append(rango_actual)

        santiago_tz = pytz.timezone('Chile/Continental')

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
        tabla_energia = [{'bus': y.bus_name, 'fecha': fecha.strftime('%Y-%m-%d'), 'energia_total': 0} for fecha in
                         dias_mes]
        complete_table = []

        # Actualizar la energía total en la tabla con los valores calculados
        for item in tabla_energia:
            for dato in datos_tabla:
                if dato['fecha_inicio'][:10] == item['fecha']:
                    item['energia_total'] += (dato['carga'] * 140) / 100

        energia_por_bus = {}

        # Llenar la estructura de datos con los valores calculados
        for item in tabla_energia:
            bus = item['bus']
            fecha = item['fecha']
            energia_total = item['energia_total']
      

            if bus not in energia_por_bus:
                energia_por_bus[bus] = [0] * len(dias_mes)  # Inicializar la lista con ceros para todos los días del mes

            # Calcular el índice del día en la lista de días del mes
            indice_dia = (datetime.strptime(fecha, '%Y-%m-%d') - primer_dia_mes).days

            # Actualizar la energía total para el día correspondiente
            energia_por_bus[bus][indice_dia] += energia_total

        # Agregar los datos de energía por bus a table_data
        for bus, energias in energia_por_bus.items():
            row = [bus] + energias
            table_data.append(row)
  

    # Después de llenar table_data con todos los datos, escribirlos en el archivo xls
    for row_index, row_data in enumerate(table_data):
        for col_index, cell_data in enumerate(row_data):
            worksheet.write(row_index, col_index, cell_data)

    workbook.save(buf)
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=filename)

@login_required(login_url='login')
def reporte_soh_flota(request):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    table_data = [
        ["Bus", "Kilometraje", 'Capacidad Bateria', 'Desgaste Bateria x km']
    ]
    filename = f'estado baterias flota :{formatted_datetime}.xls'
    buf = io.BytesIO()
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('Report')

    # Obtener los nombres de los buses y el máximo ID de BatteryHealth para cada uno
    nombres_buses_max_id = BatteryHealth.battery_health.values('bus__bus_name').annotate(max_id=Max('id'))

    # Obtener los registros asociados a los buses con el ID máximo, sin duplicados
    baterias = BatteryHealth.battery_health.filter(id__in=nombres_buses_max_id.values('max_id')).select_related('bus').order_by('bus__bus_name', 'bus__lts_odometer')

    for bateria in baterias:
        if bateria.battery_health_value < 100:
            desgaste = round(bateria.bus.lts_odometer / (100 - bateria.battery_health_value), 2)
        else:
            desgaste = 'N/A'  # O cualquier otro valor que prefieras

        row = [bateria.bus.bus_name, bateria.bus.lts_odometer, f"{bateria.battery_health_value}%", desgaste]
        table_data.append(row)

    for row_index, row_data in enumerate(table_data):
        for col_index, cell_data in enumerate(row_data):
            worksheet.write(row_index, col_index, cell_data)

    workbook.save(buf)
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=filename)   


@login_required(login_url='login')
def last_soh_report(request):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y")
    table_data = [
        ["Bus","Capacidad Bateria", "fecha"]
    ]
    filename = f'estado baterias flota :{formatted_datetime}.xls'
    buf = io.BytesIO()
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('Report')



@login_required(login_url='login')
def matriz_km_diario_flota(request):
   dbname = 'alicanto-db-dev'
   user = 'postgres'
   password = 'postgres'
   host = 'alicanto-db-v1.cyydo36bjzsy.us-west-1.rds.amazonaws.com'
   port = '5432'
   current_datetime = datetime.now()
   mes = current_datetime.month
   bus = Bus.bus.all()
   bus = bus.exclude(id__in=no_update_list)
   table_data = [
        ["Mes", "Bus", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
         "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26","27",
         "28", "29", "30", "31"]
    ]
   
   formatted_datetime = current_datetime.strftime("%d-%m-%Y")
   filename = f'matriz km diario flota :{formatted_datetime}.xls'
   buf = io.BytesIO()
   workbook = xlwt.Workbook(encoding='utf-8')
   worksheet = workbook.add_sheet('Report')
   
   for i in bus:
      bus_id = i.id
      name = i.bus_name
      connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
      cursor = connection.cursor()
      query = """
      SELECT
      CASE mes
        WHEN 1 THEN 'Enero'
        WHEN 2 THEN 'Febrero'
        WHEN 3 THEN 'Marzo'
        WHEN 4 THEN 'Abril'
        WHEN 5 THEN 'Mayo'
        WHEN 6 THEN 'Junio'
        WHEN 7 THEN 'Julio'
        WHEN 8 THEN 'Agosto'
        WHEN 9 THEN 'Septiembre'
        WHEN 10 THEN 'Octubre'
        WHEN 11 THEN 'Noviembre'
        WHEN 12 THEN 'Diciembre'
      END AS mes,
      bus_signals_bus.bus_name AS bus,
      MAX(CASE WHEN dia = 1 THEN max_odometer END) AS "1",
      MAX(CASE WHEN dia = 2 THEN max_odometer END) AS "2",
      MAX(CASE WHEN dia = 3 THEN max_odometer END) AS "3",
      MAX(CASE WHEN dia = 4 THEN max_odometer END) AS "4",
      MAX(CASE WHEN dia = 5 THEN max_odometer END) AS "5",
      MAX(CASE WHEN dia = 6 THEN max_odometer END) AS "6",
      MAX(CASE WHEN dia = 7 THEN max_odometer END) AS "7",
      MAX(CASE WHEN dia = 8 THEN max_odometer END) AS "8",
      MAX(CASE WHEN dia = 9 THEN max_odometer END) AS "9",
      MAX(CASE WHEN dia = 10 THEN max_odometer END) AS "10",
      MAX(CASE WHEN dia = 11 THEN max_odometer END) AS "11",
      MAX(CASE WHEN dia = 12 THEN max_odometer END) AS "12",
      MAX(CASE WHEN dia = 13 THEN max_odometer END) AS "13",
      MAX(CASE WHEN dia = 14 THEN max_odometer END) AS "14",
      MAX(CASE WHEN dia = 15 THEN max_odometer END) AS "15",
      MAX(CASE WHEN dia = 16 THEN max_odometer END) AS "16",
      MAX(CASE WHEN dia = 17 THEN max_odometer END) AS "17",
      MAX(CASE WHEN dia = 18 THEN max_odometer END) AS "18",
      MAX(CASE WHEN dia = 19 THEN max_odometer END) AS "19",
      MAX(CASE WHEN dia = 20 THEN max_odometer END) AS "20",
      MAX(CASE WHEN dia = 21 THEN max_odometer END) AS "21",
      MAX(CASE WHEN dia = 22 THEN max_odometer END) AS "22",
      MAX(CASE WHEN dia = 23 THEN max_odometer END) AS "23",
      MAX(CASE WHEN dia = 24 THEN max_odometer END) AS "24",
      MAX(CASE WHEN dia = 25 THEN max_odometer END) AS "25",
      MAX(CASE WHEN dia = 26 THEN max_odometer END) AS "26",
      MAX(CASE WHEN dia = 27 THEN max_odometer END) AS "27",
      MAX(CASE WHEN dia = 28 THEN max_odometer END) AS "28",
      MAX(CASE WHEN dia = 29 THEN max_odometer END) AS "29",
      MAX(CASE WHEN dia = 30 THEN max_odometer END) AS "30",
      MAX(CASE WHEN dia = 31 THEN max_odometer END) AS "31"
      FROM (
         SELECT
            EXTRACT(MONTH FROM "TimeStamp") AS mes,
            EXTRACT(DAY FROM "TimeStamp") AS dia,
            MAX(odometer_value) AS max_odometer,
            bus_id
      FROM
        bus_signals_odometer
      WHERE
        bus_id = %s
      GROUP BY
        EXTRACT(MONTH FROM "TimeStamp"),
        EXTRACT(DAY FROM "TimeStamp"),
        bus_id
               ) AS max_odometers
      LEFT JOIN bus_signals_bus ON max_odometers.bus_id = bus_signals_bus.id
      WHERE
         bus_id = %s
         AND mes = %s
         GROUP BY
         mes, bus;
      """
      cursor.execute(query, (bus_id, bus_id, mes))
      results = cursor.fetchall()
     

      if results and len(results[0]) >= 32:
        row = [results[0][0], results[0][1]]  # Agrega el mes y el bus al principio
        row.extend([value if value is not None else 0 for value in results[0][2:]])  # Agrega los valores de los días
        table_data.append(row)
      else:
        row = [mes, name, 0]  # Agrega el mes, el bus y un valor predeterminado
        table_data.append(row)

      cursor.close()
      connection.close()
       
      
   for row_index, row_data in enumerate(table_data):
    for col_index, cell_data in enumerate(row_data):
      worksheet.write(row_index, col_index, cell_data)

# Guardar el archivo Excel en el buffer
   workbook.save(buf)
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

@login_required(login_url='login')
def historical_energy_report(request):
    if request.method == 'GET':
        context = {
            'bus': Bus.bus.all().exclude(id__in=no_update_list),
            'meses2': [{'mes': 'Enero', 'numero': 1}, {'mes': 'Febrero', 'numero': 2}, {'mes': 'Marzo', 'numero': 3},
                       {'mes': 'Abril', 'numero': 4}, {'mes': 'Mayo', 'numero': 5}, {'mes': 'Junio', 'numero': 6},
                       {'mes': 'Julio', 'numero': 7}, {'mes': 'Agosto', 'numero': 8}, {'mes': 'Septiembre', 'numero': 9},
                       {'mes': 'Octubre', 'numero': 10}, {'mes': 'Noviembre', 'numero': 11}, {'mes': 'Diciembre', 'numero': 12}],
        }

        return render(request, 'reports/historicos.html', context)

    if request.method == 'POST':
        mes = int(request.POST['mes'])
        año = int(request.POST['año'])
        bus_list = Bus.bus.exclude(id__in=no_update_list)

        santiago_tz = pytz.timezone('Chile/Continental')
        lista_datos_organizados = {bus.id: {'bus': bus.bus_name, 'datos': {}} for bus in bus_list}

        charge_data = ChargeStatus.charge_status.filter(bus_id__in=bus_list.values_list('id', flat=True)).order_by('TimeStamp')

        for item in charge_data:
            bus_id = item.bus_id
            if bus_id in lista_datos_organizados:
                if item.charge_status_value == 1:
                    lista_datos_organizados[bus_id].setdefault('rango_actual', []).append(item)
                elif item.charge_status_value == 0 and 'rango_actual' in lista_datos_organizados[bus_id]:
                    rango_actual = lista_datos_organizados[bus_id].pop('rango_actual')
                    lista_datos_organizados[bus_id].setdefault('rangos', []).append(rango_actual)

        for bus_id, data in lista_datos_organizados.items():
            rangos = data.get('rangos', [])
            datos_tabla = []
            for i, rango in enumerate(rangos, 1):
                fecha_inicio = rango[0].TimeStamp
                fecha_termino = rango[-1].TimeStamp
                soc_inicial = rango[0].soc_level
                soc_final = rango[-1].soc_level
                carga = soc_final - soc_inicial
                diferencia = fecha_termino - fecha_inicio
                diferencia_en_horas = diferencia.total_seconds() / 3600
                datos_tabla.append({
                    'rango': i,
                    'fecha_inicio': fecha_inicio,
                    'fecha_termino': fecha_termino,
                    'tiempo': round(diferencia_en_horas, 2),
                    'soc_inicial': soc_inicial,
                    'soc_final': soc_final,
                    'carga': carga,
                    'energia': (carga * 140) / 100,
                    'bus': data['bus']
                })

            primer_dia_mes = datetime(año, mes, 1, tzinfo=santiago_tz)
            ultimo_dia_mes = (primer_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            dias_mes = [primer_dia_mes + timedelta(days=d) for d in range((ultimo_dia_mes - primer_dia_mes).days + 1)]

            tabla_energia = {fecha.strftime('%Y-%m-%d'): 0 for fecha in dias_mes}
            for dato in datos_tabla:
                fecha = dato['fecha_inicio'].strftime('%Y-%m-%d')
                if fecha in tabla_energia:
                    tabla_energia[fecha] += (dato['carga'] * 140) / 100

            for fecha, energia_total in tabla_energia.items():
                data['datos'][fecha] = round(energia_total, 2)

        # Generación del archivo Excel
        buf = io.BytesIO()
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Reporte')
        filename = f'energia_flota_{mes}-{año}.xls'

        # Encabezado de la primera fila
        worksheet.write(0, 0, "Bus")
        for col_num, dia in enumerate(dias_mes, start=1):
            worksheet.write(0, col_num, dia.strftime('%d'))

        # Datos de los buses
        for row_num, data in enumerate(lista_datos_organizados.values(), start=1):
            worksheet.write(row_num, 0, data['bus'])
            for fecha, energia_total in data['datos'].items():
                col_num = next((i + 1 for i, dia in enumerate(dias_mes) if fecha == dia.strftime('%Y-%m-%d')), None)
                if col_num:
                    worksheet.write(row_num, col_num, energia_total)

        workbook.save(buf)
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename=filename)

@login_required(login_url='login')
def historic_soh(request):
    if request.method == 'GET':
         return render(request, 'reports/historicos.html')
    
    if request.method == 'POST':
        dbname = 'alicanto-db-dev'
        user = 'postgres'
        password = 'postgres'
        host = 'alicanto-db-v1.cyydo36bjzsy.us-west-1.rds.amazonaws.com'
        port = '5432'
        bus = request.POST['bus']
        año = request.POST['año']
        buf = io.BytesIO()
        filename = f'soh anual id:{bus}-año:{año}.pdf' 
        doc = SimpleDocTemplate(buf, pagesize=letter)
        elements = []
        table_data = [
        ["Dia", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        ]
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = connection.cursor()

        query = """ WITH all_days AS (
             SELECT generate_series(1, 31) AS dia
                )
                SELECT
                    all_days.dia,
                    MAX(CASE WHEN mes = 1 THEN max_soh END) AS enero,
                    MAX(CASE WHEN mes = 2 THEN max_soh END) AS febrero,
                    MAX(CASE WHEN mes = 3 THEN max_soh END) AS marzo,
                    MAX(CASE WHEN mes = 4 THEN max_soh END) AS abril,
                    MAX(CASE WHEN mes = 5 THEN max_soh END) AS mayo,
                    MAX(CASE WHEN mes = 6 THEN max_soh END) AS junio,
                    MAX(CASE WHEN mes = 7 THEN max_soh END) AS julio,
                    MAX(CASE WHEN mes = 8 THEN max_soh END) AS agosto,
                    MAX(CASE WHEN mes = 9 THEN max_soh END) AS septiembre,
                    MAX(CASE WHEN mes = 10 THEN max_soh END) AS octubre,
                    MAX(CASE WHEN mes = 11 THEN max_soh END) AS noviembre,
                    MAX(CASE WHEN mes = 12 THEN max_soh END) AS diciembre
                FROM all_days
                LEFT JOIN (
                    SELECT
                        EXTRACT(DAY FROM "TimeStamp") AS dia,
                        bus_id,
                        battery_health_value as max_soh,
                        EXTRACT(MONTH FROM "TimeStamp") AS mes,
                        EXTRACT(YEAR FROM "TimeStamp") AS año
                    FROM (
                        WITH ranked_data AS (
                            SELECT
                                bus_id,
                                battery_health_value,
                                "TimeStamp",
                                ROW_NUMBER() OVER (PARTITION BY bus_id, DATE_TRUNC('day', "TimeStamp") ORDER BY battery_health_value DESC) AS rnk
                            FROM
                                bus_signals_batteryhealth
                        )
                        SELECT
                            bus_id,
                            battery_health_value,
                            "TimeStamp"
                        FROM
                            ranked_data
                        WHERE
                            rnk = 1
                        ORDER BY
                            bus_id, "TimeStamp" DESC
                    ) A
                    WHERE bus_id = %s

                ) A ON all_days.dia = A.dia
                WHERE año = %s
                GROUP BY all_days.dia; 
                """
        cursor.execute(query, (bus, año))
        result = cursor.fetchall()

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

@login_required(login_url='login')
def last_value_cells_deltas(request):
    dbname = 'alicanto-db-dev'
    user = 'postgres'
    password = 'postgres'
    host = 'alicanto-db-v1.cyydo36bjzsy.us-west-1.rds.amazonaws.com'
    port = '5432'   
    buf = io.BytesIO()
    bus = Bus.bus.all()
    filename = 'last_value_cells_deltas_flota.pdf' 
    doc = SimpleDocTemplate(buf, pagesize=letter)
    elements = []
    table_data = [[
            "Bus", "Max Voltaje", "Min Voltaje", "Prom Voltaje" ,"Δ Min/Max"
        ]]
    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor = connection.cursor()
    for i in bus:
        bus_id = i.id
        query = """SELECT *
                   FROM bus_signals_cellsvoltage
                   WHERE bus_id = %s
                   ORDER BY "TimeStamp" DESC
                   LIMIT 1;"""
        cursor.execute(query, (bus_id,))
        results = cursor.fetchall()
        
        if results:
            row = [
                i.bus_name, 
                results[0][2], 
                results[0][3], 
                results[0][4], 
                round(results[0][2] - results[0][3], 4)
            ]
            table_data.append(row)
        else:
            print(f"No se encontraron resultados para el bus {i.bus_name}.")

    # Estilo de la tabla
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    # Agregar título
    styles = getSampleStyleSheet()
    title = Paragraph("Reporte de Últimos Valores de Voltaje de Celdas Flota", styles['Title'])
    elements.append(title)
    
    # Agregar la tabla al PDF
    elements.append(table)
    
    # Construir el PDF
    doc.build(elements)
    
    # Configurar el buffer para que FileResponse pueda leerlo
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)

@login_required(login_url='login')
def last_value_cells_deltas_excel(request):
    dbname = 'alicanto-db-dev'
    user = 'postgres'
    password = 'postgres'
    host = 'alicanto-db-v1.cyydo36bjzsy.us-west-1.rds.amazonaws.com'
    port = '5432'   
    bus = Bus.bus.all()
    
    # Crear un nuevo Workbook de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Last Value Cells Deltas"
    
    # Especificar el nombre del archivo
    filename = 'last_value_cells_deltas_flota.xlsx' 
    
    # Encabezado de la hoja
    headers = ["Bus", "Max Voltaje", "Min Voltaje", "Prom Voltaje", "Δ Min/Max"]
    ws.append(headers)
    
    # Conectar a la base de datos
    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor = connection.cursor()
    
    for i in bus:
        bus_id = i.id
        query = """SELECT *
                   FROM bus_signals_cellsvoltage
                   WHERE bus_id = %s
                   ORDER BY "TimeStamp" DESC
                   LIMIT 1;"""
        cursor.execute(query, (bus_id,))
        results = cursor.fetchall()
        
        if results:
            row = [
                i.bus_name, 
                results[0][2], 
                results[0][3], 
                results[0][4], 
                round(results[0][2] - results[0][3], 4)
            ]
            ws.append(row)
        else:
            print(f"No se encontraron resultados para el bus. {i.bus_name}.")
    
    # Guardar el archivo en un buffer
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    
    # Retornar el archivo Excel como un FileResponse
    return FileResponse(buf, as_attachment=True, filename=filename)
    
@login_required(login_url='login')
def bus_performance_report_excel(request, pk):
    montly_result = monthly_bus_km(pk)
    bus = Bus.bus.get(pk=pk)
    current_datetime = timezone.now()
    mes_actual = current_datetime.strftime('%m')
    charge_data = ChargeStatus.charge_status.filter(bus_id=pk).order_by('TimeStamp')
    rangos = []
    rango_actual = []
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

# Comenzamos con rendimiento --------------------------------------------------------->
    monthly_totals_dict = {item['month']: item['energy'] for item in monthly_totals}
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
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Rendimiento Bus"
    filename = "Rendimiento Bus f'{bus.bus_name}'.xlsx"
    headers = ["Mes", "Recorrido KM", "Energia KWH", "Rendimiento KWH/KM"]
    ws.append(headers)
    for i in combined_data:
        if combined_data:
            ws.append([i['month'], i['difference'], i['energy'], i['rendimiento']])
        else:
            print(f"No se encontraron resultados para el bus. {i.bus_name}.")
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)

@login_required(login_url='login')
def switch_report_xls(request, pk):
    selected_bus = pk
    bus = Bus.bus.get(id=selected_bus)
    switch_state = EcuState.ecu_state.filter(bus_id=selected_bus).order_by('-TimeStamp')
    ranges = []
    rango = 0
    start_time = None
    for record in switch_state:
        # Accede a los campos del modelo directamente
        if record.sleep_state == 0 and start_time is None:
            start_time = record.TimeStamp  # Inicia el rango con la primera aparición de 0
        elif record.sleep_state != 0 and start_time is not None:
            end_time = record.TimeStamp  # Finaliza el rango con el primer valor diferente de 0
            rango += 1
            # Calcula la diferencia entre las fechas
            periodo = start_time - end_time
            # Convierte el periodo a minutos
            minutos = periodo.total_seconds() / 60
            hrs = minutos / 60
            # Almacena las fechas formateadas y el periodo en minutos
            ranges.append({
                "rango": rango,
                "inicio": format_date(end_time),
                "final": format_date(start_time),
                "periodo": f"{hrs:.2f} hrs"  # Formateamos el resultado en hrs
            })
            start_time = None  # Resetea para el siguiente rango
    wb = Workbook()
    ws = wb.active
    filename = f"Reporte Estado EcuSleep Bus '{bus.bus_name}'.xlsx"
    ws.title = f"Reporte Estado Ecu Sleep Bus '{bus.bus_name}'"
    headers = ["Rango", "Inicio", "Final", "Periodo Hrs"]
    ws.append(headers)
    for i in ranges:
        if ranges:
            ws.append([i['rango'], i['inicio'], i['final'], i['periodo']])
        else:
            print(f"No se encontraron resultados para el bus.")
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)

    
    return print("Generando reporte de switches...")
    
    
def drive_report(request, pk):
    selected_bus = pk
    bus = Bus.bus.get(id=selected_bus)
    drive_state = EcuState.ecu_state.filter(bus_id=selected_bus).order_by('-TimeStamp')
    ranges = []
    rango = 0
    start_time = None
    for record in drive_state:
        # Accede a los campos del modelo directamente
        if record.sleep_state == 9 and start_time is None:
            start_time = record.TimeStamp  # Inicia el rango con la primera aparición de 0
        elif record.sleep_state != 9 and start_time is not None:
            end_time = record.TimeStamp  # Finaliza el rango con el primer valor diferente de 0
            rango += 1
            # Calcula la diferencia entre las fechas
            periodo = start_time - end_time
            # Convierte el periodo a minutos
            minutos = periodo.total_seconds() / 60
            hrs = minutos / 60
            # Almacena las fechas formateadas y el periodo en minutos
            ranges.append({
                "rango": rango,
                "inicio": format_date(end_time),
                "final": format_date(start_time),
                "periodo": f"{hrs:.2f} hrs"  # Formateamos el resultado en hrs
            })
            start_time = None  # Resetea para el siguiente rango
    wb = Workbook()
    ws = wb.active
    filename = f"Reporte Estado Drive Bus '{bus.bus_name}'.xlsx"
    ws.title = f"Reporte Estado Drive Bus '{bus.bus_name}'"
    headers = ["Rango", "Inicio", "Final", "Periodo Hrs"]
    ws.append(headers)
    for i in ranges:
        if ranges:
            ws.append([i['rango'], i['inicio'], i['final'], i['periodo']])
        else:
            print(f"No se encontraron resultados para el bus.")
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=filename)
    
