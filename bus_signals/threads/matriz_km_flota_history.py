from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from bus_signals.models import Bus, Odometer
from django.db.models.functions import ExtractMonth, ExtractDay, ExtractYear
from django.db.models import Max
from reports.models import MatrizKmFlotaHistorico

from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone


no_update_list = ['24', '87', '61', '87', '137', '132', '134', '133', '130', '129', '128', '131', '136', '135']


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

def get_historical_data(mes, año):
    # Filtrar buses excluyendo los de la lista no actualizable
    buses = Bus.bus.all().exclude(id__in=no_update_list)
    historical_data = []

    with transaction.atomic():
        for bus in buses:
            # Obtener datos del odómetro agrupando por día y obteniendo el máximo
            odometer_data = (
                Odometer.odometer
                .filter(
                    bus_id=bus.id,
                    TimeStamp__year=año,
                    TimeStamp__month=mes
                )
                .annotate(dia=ExtractDay('TimeStamp'))
                .values('dia')
                .annotate(max_odometer=Max('odometer_value'))
            )

            for data in odometer_data:
                # Guardar cada registro en el modelo
                MatrizKmFlotaHistorico.objects.create(
                    bus=bus,
                    dia=data['dia'],
                    mes=mes,
                    año=año,
                    km_value=data['max_odometer']
                )
                historical_data.append({
                    'bus': bus,
                    'dia': data['dia'],
                    'mes': mes,
                    'año': año,
                    'km_value': data['max_odometer']
                })

            

    return historical_data


@scheduler.scheduled_job(CronTrigger(day='last', hour=23, minute=30, timezone='America/Santiago'))
def scheduled_get_historical_data():
    # Aquí puedes pasar el mes y el año que necesites
    now = timezone.now()
    mes = now.month
    año = now.year
    get_historical_data(mes, año)

def start():
    scheduler.start()
