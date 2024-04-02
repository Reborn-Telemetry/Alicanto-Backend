from django.shortcuts import render
from bus_signals.query_utils import matriz_km_diario_flota
from bus_signals.models import Bus
from . models import Prueba
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

import requests
no_update_list = ['27','34', '60', '24', '87', '116', '21', '61', '82', '83', '81']

# Create your views here.
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
   prueba = Prueba.objects.all()
   context= {'prueba': prueba}
   print(bus_fs) 
   print(bus_operativo)
   return render(request, 'reports/disponibilidad_flota.html', context)


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