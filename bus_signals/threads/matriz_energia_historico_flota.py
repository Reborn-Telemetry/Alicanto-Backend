from datetime import datetime
from datetime import datetime, timedelta

from django.db import transaction
import pytz
from django.http import JsonResponse
from django.shortcuts import render
from bus_signals.models import Bus, Odometer, ChargeStatus
from django.db.models.functions import ExtractMonth, ExtractDay, ExtractYear
from django.db.models import Max
from reports.models import MatrizEnergiaFlotaHistorico

from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone


no_update_list = ['24', '87', '61', '87', '137', '132', '134', '133', '130', '129', '128', '131', '136', '135']


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def save_historical_energy_data(mes, año):
    bus_list = Bus.bus.exclude(id__in=no_update_list)

    # Obtener la zona horaria de Santiago
    santiago_tz = pytz.timezone('Chile/Continental')

    # Calcular el primer y último día del mes
    primer_dia_mes = datetime(año, mes, 1, tzinfo=santiago_tz)
    if mes == 12:
        ultimo_dia_mes = datetime(año + 1, 1, 1, tzinfo=santiago_tz) - timedelta(days=1)
    else:
        ultimo_dia_mes = datetime(año, mes + 1, 1, tzinfo=santiago_tz) - timedelta(days=1)

    # Filtrar ChargeStatus por el mes y año
    charge_data = ChargeStatus.charge_status.filter(
        bus_id__in=bus_list.values_list('id', flat=True),
        TimeStamp__gte=primer_dia_mes,
        TimeStamp__lte=ultimo_dia_mes
    ).order_by('TimeStamp')

    lista_datos_organizados = {bus.id: {'bus': bus, 'datos': {}} for bus in bus_list}

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
            

        # Guardar en MatrizEnergiaFlotaHistorico
        tabla_energia = {fecha.strftime('%Y-%m-%d'): 0 for fecha in (primer_dia_mes + timedelta(days=d) for d in range((ultimo_dia_mes - primer_dia_mes).days + 1))}
        for dato in datos_tabla:
            fecha = dato['fecha_inicio'].strftime('%Y-%m-%d')
            if fecha in tabla_energia:
                tabla_energia[fecha] += dato['energia']

        with transaction.atomic():
            for fecha, energia_total in tabla_energia.items():
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                MatrizEnergiaFlotaHistorico.objects.create(
                    bus=data['bus'],
                    dia=fecha_obj.day,
                    mes=mes,
                    año=año,
                    energia=round(energia_total, 2)
                )
                

    return "Datos de energía histórica guardados correctamente."


@scheduler.scheduled_job(CronTrigger(day='last', hour=23, minute=50, timezone='America/Santiago'))
def scheduled_get_historical_data():
    # Aquí puedes pasar el mes y el año que necesites
    now = timezone.now()
    mes = now.month
    año = now.year
    save_historical_energy_data(mes, año)

def begin():
    scheduler.start()