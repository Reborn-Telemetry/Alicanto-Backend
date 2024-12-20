from django.db.models import Min, Max
from datetime import datetime
from bus_signals.models import Odometer, Bus
from reports.models import Recorrido
from django.utils import timezone
from apscheduler.triggers.cron import CronTrigger
import pytz

def calcular_recorridos_por_dia(dia, mes, año):
    # Definimos el rango de tiempo para el día específico
    start_date = datetime(año, mes, dia, 0, 0, 0)
    end_date = datetime(año, mes, dia, 23, 59, 59)
    
    # Agrupamos por bus y seleccionamos el primer y último valor del odómetro del día
    odometer_values = (
        Odometer.odometer
        .filter(TimeStamp__range=(start_date, end_date))
        .values('bus')
        .annotate(
            min_odometer=Min('odometer_value'),
            max_odometer=Max('odometer_value')
        )
    )

    # Insertamos o actualizamos los registros en `Recorrido` sin calcular `recorrido` explícitamente
    for entry in odometer_values:
        # Obtenemos el registro de inicio (primer TimeStamp del día) y el registro de final (último TimeStamp del día)
        min_entry = (
            Odometer.odometer
            .filter(bus_id=entry['bus'], TimeStamp__range=(start_date, end_date))
            .order_by('TimeStamp')
            .first()
        )
        max_entry = (
            Odometer.odometer
            .filter(bus_id=entry['bus'], TimeStamp__range=(start_date, end_date))
            .order_by('-TimeStamp')
            .first()
        )
        
        # Verificamos que existen ambos registros antes de proceder
        if min_entry and max_entry:
            Recorrido.objects.update_or_create(
                bus_id=entry['bus'],
                dia=dia,
                mes=mes,
                año=año,
                defaults={
                    'min_odometer': min_entry.odometer_value,
                    'max_odometer': max_entry.odometer_value,
                }
            )
    
    return odometer_values


def daily_recorrido_update():
    # Obtener la fecha y hora actuales
    now = timezone.now().astimezone(pytz.timezone('America/Santiago'))
    mes = now.month
    año = now.year
    dia = now.day
    # Llamar a la función que realiza la consulta y guarda los datos del odómetro
    calcular_recorridos_por_dia(dia, mes, año)


def iniciar_calculo_recorrido_diario(scheduler):
    # Configurar el trigger para que se ejecute todos los días a las 23:55 horas
    scheduler.add_job(
        daily_recorrido_update,
        trigger=CronTrigger(hour=23, minute=58, timezone=pytz.timezone('America/Santiago')),
        id="daily_recorrido_update",
        replace_existing=True,
    )
