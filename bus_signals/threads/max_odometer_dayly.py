from django.db.models import Max
from datetime import datetime
from bus_signals.models import Odometer
from reports.models import DailyMatrizKmAutoReport
from datetime import datetime, timedelta
from django.db import transaction
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


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

@scheduler.scheduled_job(CronTrigger(day='last', hour=23, minute=30, timezone='America/Santiago'))
def daily_max_auto_update():
    now = timezone.now()
    mes = now.month
    año = now.year
    dia = now.day
    get_max_odometer_per_day_and_month(dia, mes, año)