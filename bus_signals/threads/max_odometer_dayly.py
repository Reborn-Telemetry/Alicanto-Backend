from django.db.models import Max
from datetime import datetime
from bus_signals.models import Odometer
from reports.models import DailyMatrizKmAutoReport
from django.db import transaction
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
import pytz


def get_max_odometer_per_day_and_month(day, month, year):
    # Filtramos los registros por el día, mes y año pasados como argumentos
    start_date = datetime(year, month, day)
    end_date = start_date.replace(hour=23, minute=59, second=59)
    
    # Realizamos la consulta que filtra por rango de fecha y agrupa por bus, tomando el valor máximo de odometer_value
    odometer_max_values = Odometer.odometer.filter(
        TimeStamp__range=(start_date, end_date)
    ).values('bus').annotate(max_odometer_value=Max('odometer_value'))
    
    # Comprobamos si la consulta devuelve datos
    if not odometer_max_values:
        print("No se encontraron datos para el día especificado.")
    
    # Guardamos los resultados en el modelo DailyMatrizKmAutoReport
    for entry in odometer_max_values:
        DailyMatrizKmAutoReport.objects.create(
            bus_id=entry['bus'],          # Utilizamos el ID del bus
            dia=day,
            mes=month,
            año=year,
            max_odometer=entry['max_odometer_value']
        )
    
    return odometer_max_values


def daily_max_auto_update():
    # Obtener la fecha y hora actuales
    now = timezone.now().astimezone(pytz.timezone('America/Santiago'))
    mes = now.month
    año = now.year
    dia = now.day
    # Llamar a la función que realiza la consulta y guarda los datos del odómetro
    get_max_odometer_per_day_and_month(dia, mes, año)


def iniciar_calculo_odometro_diario(scheduler):
    # Configurar el trigger para que se ejecute todos los días a las 23:30 horas
    scheduler.add_job(
        daily_max_auto_update,
        trigger=CronTrigger(hour=23, minute=55, timezone=pytz.timezone('America/santiago')),
        id="daily_max_auto_update",
        replace_existing=True,
    )
