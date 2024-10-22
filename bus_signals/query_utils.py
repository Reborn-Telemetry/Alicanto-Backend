import psycopg2
from django.db.models import Max
from django.db.models.functions import ExtractMonth
from bus_signals.models import Odometer, BatteryHealth
from collections import defaultdict
from reports.models import DailyMatrizKmAutoReport

dbname = 'alicanto-db-dev'
user = 'postgres'
password = 'postgres'
host = 'alicanto-db-v1.cyydo36bjzsy.us-west-1.rds.amazonaws.com'
port = '5432'

def format_date(date):
        return date.strftime('%d-%m-%Y %H:%M:%S')

def daily_bus_km(bus_id, year):
    # Inicializar un diccionario para almacenar los resultados por día y mes
    result = defaultdict(lambda: [None] * 12)  # Un array de 12 meses (None para cada mes)

    # Obtener los datos del modelo para el bus y el año específico
    km_data = DailyMatrizKmAutoReport.objects.filter(bus_id=bus_id, año=year).values('dia', 'mes', 'max_odometer')

    # Recorrer los resultados y llenar el diccionario
    for data in km_data:
        dia = data['dia'] - 1  # Los días van de 1 a 31, ajustamos el índice
        mes = data['mes'] - 1  # Los meses van de 1 a 12, ajustamos el índice
        result[dia][mes] = data['max_odometer']  # Llenar el odómetro en el mes correspondiente

    # Convertir el diccionario en una lista de listas (un formato más manejable para el template)
    result_list = [[dia + 1] + values for dia, values in result.items()]  # El día es el primer valor de la fila

    return result_list


def monthly_bus_km(id_bus):
     
     connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
     cursor = connection.cursor()
     query = """SELECT C.bus_name, ENE_MIN, B.ENE_MAX, FEB_MIN, B.FEB_MAX, MAR_MIN, B.MAR_MAX, ABR_MIN, B.ABR_MAX, MAY_MIN, B.MAY_MAX, JUN_MIN, B.JUN_MAX, AGO_MIN, B.AGO_MAX, SEPT_MIN, B.SEPT_MAX, OCT_MIN, B.OCT_MAX, NOV_MIN, B.NOV_MAX, DIC_MIN, B.DIC_MAX

FROM
(SELECT
    bus_id,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 1 THEN odometer_value END) AS ENE_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 2 THEN odometer_value END) AS FEB_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 3 THEN odometer_value END) AS MAR_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 4 THEN odometer_value END) AS ABR_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 5 THEN odometer_value END) AS MAY_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 6 THEN odometer_value END) AS JUN_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 7 THEN odometer_value END) AS JUL_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 8 THEN odometer_value END) AS AGO_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 9 THEN odometer_value END) AS SEPT_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 10 THEN odometer_value END) AS OCT_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 11 THEN odometer_value END) AS NOV_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 12 THEN odometer_value END) AS DIC_MIN
FROM
    (WITH ranked_data AS (
        SELECT
            bus_id,
            odometer_value,
            "TimeStamp" as fecha,
            ROW_NUMBER() OVER (PARTITION BY bus_id, DATE_TRUNC('month', "TimeStamp") ORDER BY odometer_value ASC) AS rnk_low
        FROM
            bus_signals_odometer
        )
        SELECT
            bus_id,
            odometer_value,
            fecha
        FROM
            ranked_data
        WHERE
            rnk_low = 1
    ) A
GROUP BY
    bus_id) A

LEFT JOIN (

SELECT
    bus_id,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 1 THEN odometer_value END) AS ENE_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 2 THEN odometer_value END) AS FEB_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 3 THEN odometer_value END) AS MAR_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 4 THEN odometer_value END) AS ABR_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 5 THEN odometer_value END) AS MAY_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 6 THEN odometer_value END) AS JUN_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 7 THEN odometer_value END) AS JUL_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 8 THEN odometer_value END) AS AGO_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 9 THEN odometer_value END) AS SEPT_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 10 THEN odometer_value END) AS OCT_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 11 THEN odometer_value END) AS NOV_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 12 THEN odometer_value END) AS DIC_MAX
FROM
    (WITH ranked_data AS (
        SELECT
            bus_id,
            odometer_value,
            "TimeStamp" as fecha,
            ROW_NUMBER() OVER (PARTITION BY bus_id, DATE_TRUNC('month', "TimeStamp") ORDER BY odometer_value DESC) AS rnk_high
        FROM
            bus_signals_odometer
        )
        SELECT
            bus_id,
            odometer_value,
            fecha
        FROM
            ranked_data
        WHERE
            rnk_high = 1
    ) A
GROUP BY
    bus_id) B on A.bus_id=B.bus_id
left join bus_signals_bus C on A.bus_id=C.id
where A.bus_id=%s
ORDER BY C.bus_name"""

     cursor.execute(query, (id_bus,))
     results = cursor.fetchall()
     cursor.close()
     connection.close()
     return results
     
    

    

def monthly_fleet_km():
    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor = connection.cursor()
    query = """SELECT C.bus_name, ENE_MIN, B.ENE_MAX, FEB_MIN, B.FEB_MAX, MAR_MIN, B.MAR_MAX, ABR_MIN, B.ABR_MAX, MAY_MIN, B.MAY_MAX, JUN_MIN, B.JUN_MAX, AGO_MIN, B.AGO_MAX, SEPT_MIN, B.SEPT_MAX, OCT_MIN, B.OCT_MAX, NOV_MIN, B.NOV_MAX, DIC_MIN, B.DIC_MAX
FROM
(SELECT
    bus_id,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 1 THEN odometer_value END) AS ENE_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 2 THEN odometer_value END) AS FEB_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 3 THEN odometer_value END) AS MAR_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 4 THEN odometer_value END) AS ABR_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 5 THEN odometer_value END) AS MAY_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 6 THEN odometer_value END) AS JUN_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 7 THEN odometer_value END) AS JUL_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 8 THEN odometer_value END) AS AGO_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 9 THEN odometer_value END) AS SEPT_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 10 THEN odometer_value END) AS OCT_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 11 THEN odometer_value END) AS NOV_MIN,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 12 THEN odometer_value END) AS DIC_MIN
FROM
    (WITH ranked_data AS (
        SELECT
            bus_id,
            odometer_value,
            "TimeStamp" as fecha,
            ROW_NUMBER() OVER (PARTITION BY bus_id, DATE_TRUNC('month', "TimeStamp") ORDER BY odometer_value ASC) AS rnk_low
        FROM
            bus_signals_odometer
        )
        SELECT
            bus_id,
            odometer_value,
            fecha
        FROM
            ranked_data
        WHERE
            rnk_low = 1
    ) A
GROUP BY
    bus_id) A
LEFT JOIN (
SELECT
    bus_id,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 1 THEN odometer_value END) AS ENE_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 2 THEN odometer_value END) AS FEB_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 3 THEN odometer_value END) AS MAR_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 4 THEN odometer_value END) AS ABR_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 5 THEN odometer_value END) AS MAY_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 6 THEN odometer_value END) AS JUN_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 7 THEN odometer_value END) AS JUL_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 8 THEN odometer_value END) AS AGO_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 9 THEN odometer_value END) AS SEPT_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 10 THEN odometer_value END) AS OCT_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 11 THEN odometer_value END) AS NOV_MAX,
    MAX(CASE WHEN EXTRACT(MONTH FROM fecha) = 12 THEN odometer_value END) AS DIC_MAX
FROM
    (WITH ranked_data AS (
        SELECT
            bus_id,
            odometer_value,
            "TimeStamp" as fecha,
            ROW_NUMBER() OVER (PARTITION BY bus_id, DATE_TRUNC('month', "TimeStamp") ORDER BY odometer_value DESC) AS rnk_high
        FROM
            bus_signals_odometer
        )
        SELECT
            bus_id,
            odometer_value,
            fecha
        FROM
            ranked_data
        WHERE
            rnk_high = 1
    ) A
GROUP BY
    bus_id) B on A.bus_id=B.bus_id
left join bus_signals_bus C on A.bus_id=C.id    
    ORDER BY C.bus_name;"""
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results


def dinamic_query(dia, mes, id_bus):
    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor = connection.cursor()
    query ="""WITH all_days AS (
SELECT generate_series(1, 31) AS dia
)
SELECT
all_days.dia,

LAST_VALUE(CASE WHEN mes = 1 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS enero,
LAST_VALUE(CASE WHEN mes = 2 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS febrero,
LAST_VALUE(CASE WHEN mes = 3 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS marzo,
LAST_VALUE(CASE WHEN mes = 4 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS abril,
LAST_VALUE(CASE WHEN mes = 5 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS mayo,
LAST_VALUE(CASE WHEN mes = 6 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS junio,
LAST_VALUE(CASE WHEN mes = 7 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS julio,
LAST_VALUE(CASE WHEN mes = 8 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS agosto,
LAST_VALUE(CASE WHEN mes = 9 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS septiembre,
LAST_VALUE(CASE WHEN mes = 10 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS octubre,
LAST_VALUE(CASE WHEN mes = 11 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS noviembre,
LAST_VALUE(CASE WHEN mes = 12 THEN max_odometer END) OVER (PARTITION BY all_days.dia ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS diciembre
FROM
all_days

LEFT JOIN (
SELECT
EXTRACT(DAY FROM "TimeStamp") AS dia,

bus_id,
odometer_value as max_odometer,
EXTRACT(MONTH FROM "TimeStamp") AS mes
FROM
(
WITH ranked_data AS (
SELECT
bus_id,
odometer_value,
"TimeStamp",
ROW_NUMBER() OVER (PARTITION BY bus_id, DATE_TRUNC('day', "TimeStamp") ORDER BY odometer_value DESC) AS rnk
FROM
bus_signals_odometer
)
SELECT
bus_id,
odometer_value,
"TimeStamp"
FROM
ranked_data
WHERE
rnk = 1
ORDER BY
bus_id, "TimeStamp" DESC
) A WHERE bus_id =3 AND EXTRACT(DAY FROM "TimeStamp")=27 AND EXTRACT(MONTH FROM "TimeStamp")=1
) A ON all_days.dia = A.dia;"""
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

    
def matriz_km_diario_flota(bus_id, mes):
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
    cursor.close()
    connection.close()
    return results


def get_max_odometer_per_month(bus_id):
    max_values_per_month = (
        Odometer.odometer
        .filter(bus_id=bus_id)
        .annotate(month=ExtractMonth('TimeStamp'))
        .values('month')
        .annotate(max_odometer_value=Max('odometer_value'))
        .order_by('month')  # Asegúrate de que los resultados estén ordenados por mes
    )

    # Convertir directamente a un diccionario usando dict comprehension
    return {entry['month']: entry['max_odometer_value'] for entry in max_values_per_month}




def km_flota():
     connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
     cursor = connection.cursor()
     query = """SELECT sum(max_odometer_value) AS total_odometer_value
                FROM
                (SELECT
                    bus_id,
                MAX(odometer_value) AS max_odometer_value

                FROM
                (WITH ranked_data AS (
                SELECT
                bus_id,
                odometer_value,
                ROW_NUMBER() OVER (PARTITION BY bus_id ORDER BY odometer_value DESC) AS rnk_high
                FROM
                bus_signals_odometer
                )
                SELECT
                bus_id,
                odometer_value
                FROM
                    ranked_data
                WHERE
                    rnk_high = 1
                    ) A
                GROUP BY
                    bus_id) B"""
     cursor.execute(query)
     results = cursor.fetchall()
     cursor.close()
     connection.close()
     return results

def obtener_ultimo_valor_energia(lista_datos):
    ultimo_valor_por_bus = {}
    for datos_bus in lista_datos:
        bus = datos_bus['bus']
        datos = datos_bus['datos']
        ultimo_valor = None
        for dato in reversed(datos):
            if dato['energia_total'] != '0.0':
                ultimo_valor = dato['energia_total']
                break
        if ultimo_valor is not None:
            if bus not in ultimo_valor_por_bus:
                ultimo_valor_por_bus[bus] = ultimo_valor
    
    return ultimo_valor_por_bus


def get_battery_health_report(bus_id):
    health_report = {}
    healt_values = []
    
    # Obtener los datos de BatteryHealth para el bus específico
    bus_battery_historic_health = BatteryHealth.battery_health.filter(bus=bus_id).order_by('TimeStamp')
    
    if bus_battery_historic_health.exists():
        # Formatear el inicio y fin
        health_report['inicio'] = bus_battery_historic_health.first().TimeStamp.strftime('%d/%m/%Y %H:%M')
        health_report['fin'] = bus_battery_historic_health.last().TimeStamp.strftime('%d/%m/%Y %H:%M')

        # Agregar los valores distintos a healt_values junto con su timestamp formateado
        previous_value = None
        for i in bus_battery_historic_health:
            if i.battery_health_value != previous_value:
                healt_values.append((i.TimeStamp.strftime('%d/%m/%Y %H:%M'), i.battery_health_value))
                previous_value = i.battery_health_value
        
        health_report['values'] = healt_values

    return health_report

def get_monthly_kilometer_data(bus_id, year):
    # Diccionario con los nombres de los meses
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
    
    # Crear un diccionario para almacenar los resultados
    monthly_data = {}
    
    # Iteramos sobre los 12 meses
    for month in range(1, 13):
        # Obtener el valor del odómetro el primer día del mes
        first_day_data = DailyMatrizKmAutoReport.objects.filter(bus_id=bus_id, mes=month, año=year, dia=1).first()
        
        # Obtener el valor del odómetro el último día del mes
        last_day_data = DailyMatrizKmAutoReport.objects.filter(bus_id=bus_id, mes=month, año=year).order_by('-dia').first()
        
        if first_day_data and last_day_data:
            kilometro1 = first_day_data.max_odometer
            kilometro_last_day = last_day_data.max_odometer
            recorrido = kilometro_last_day - kilometro1
            
            # Guardamos los valores en el diccionario con el nombre del mes
            monthly_data[months_dict[month]] = {
                'kilometro1': kilometro1,
                'kilometro_last_day': kilometro_last_day,
                'recorrido': recorrido
            }
        else:
            # Si no hay datos para este mes, asignamos None o algún valor indicador
            monthly_data[months_dict[month]] = {
                'kilometro1': None,
                'kilometro_last_day': None,
                'recorrido': None
            }
    
    return monthly_data