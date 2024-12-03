from django.db.models import Max
from datetime import datetime, timedelta
from django.utils import timezone
from bus_signals.models import Odometer
from reports.models import DailyMatrizKmAutoReport
from apscheduler.triggers.cron import CronTrigger
import pytz


def update_max_odometer_past_days():
    # Obtener la fecha actual y el inicio del mes en curso
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Iterar sobre cada día desde el inicio del mes hasta el día actual (excluyendo hoy)
    for day in range(1, now.day):
        current_date = start_of_month + timedelta(days=day - 1)
        next_date = current_date + timedelta(days=1)

        # Consulta para obtener los valores máximos del odómetro para cada bus en el día iterado
        odometer_max_values = Odometer.odometer.filter(
            TimeStamp__range=(current_date, next_date)
        ).values('bus').annotate(max_odometer_value=Max('odometer_value'))

        for entry in odometer_max_values:
            bus_id = entry['bus']
            max_odometer_value = entry['max_odometer_value']
            
            # Intentar obtener un registro existente para el día, mes, año y bus
            report, created = DailyMatrizKmAutoReport.objects.get_or_create(
                bus_id=bus_id,
                dia=current_date.day,
                mes=current_date.month,
                año=current_date.year,
                defaults={'max_odometer': max_odometer_value}
            )

            if not created:  # Si el registro ya existía
                # Comprobar si el valor nuevo es mayor que el existente
                if max_odometer_value > report.max_odometer:
                    report.max_odometer = max_odometer_value
                    report.save()  # Actualizar el registro con el nuevo valor
  
def iniciar_actualizacion_odometro_pasado(scheduler):
    # Configurar el trigger para que se ejecute todos los días a las 23:45
    scheduler.add_job(
        update_max_odometer_past_days,
        trigger=CronTrigger(hour=23, minute=45, timezone=pytz.timezone('America/Santiago')),
        id="update_max_odometer_past_days",
        replace_existing=True,
    )