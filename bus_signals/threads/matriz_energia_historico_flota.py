from datetime import datetime
from django.db import transaction
import pytz
from django.utils import timezone
from bus_signals.models import Bus, ChargeStatus
from reports.models import MatrizEnergiaFlotaHistorico
from apscheduler.triggers.cron import CronTrigger

no_update_list = ['87', '137', '132', '134', '133', '130', '129', '128', '131', '136', '135']

def save_historical_energy_data(dia, mes, año):
    bus_list = Bus.bus.exclude(id__in=no_update_list)

    # Obtener la zona horaria de Santiago
    santiago_tz = pytz.timezone('America/Santiago')

    # Calcular el primer y último momento del día específico
    inicio_dia = datetime(año, mes, dia, 0, 0, 0, tzinfo=santiago_tz)
    fin_dia = datetime(año, mes, dia, 23, 59, 59, tzinfo=santiago_tz)

    # Filtrar ChargeStatus por el día específico
    charge_data = ChargeStatus.charge_status.filter(
        bus_id__in=bus_list.values_list('id', flat=True),
        TimeStamp__gte=inicio_dia,
        TimeStamp__lte=fin_dia
    ).order_by('TimeStamp')

    # Verificar si la consulta no encontró resultados
    if not charge_data.exists():
        print(f"No se encontraron datos de carga para el día {dia}/{mes}/{año}.")
        return f"No se encontraron datos de carga para el día {dia}/{mes}/{año}."

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

            # Cálculo diferenciado de la energía según la serie del bus
            energia = (carga * 140) / 100 if data['bus'].bus_series == 'Queltehue' else (carga * 280) / 100

            datos_tabla.append({
                'rango': i,
                'fecha_inicio': fecha_inicio,
                'fecha_termino': fecha_termino,
                'tiempo': round(diferencia_en_horas, 2),
                'soc_inicial': soc_inicial,
                'soc_final': soc_final,
                'carga': carga,
                'energia': energia,
                'bus': data['bus']
            })
            print(datos_tabla)

        # Guardar en MatrizEnergiaFlotaHistorico
        tabla_energia = {inicio_dia.strftime('%Y-%m-%d'): 0}
        for dato in datos_tabla:
            fecha = dato['fecha_inicio'].strftime('%Y-%m-%d')
            if fecha in tabla_energia:
                tabla_energia[fecha] += dato['energia']

        with transaction.atomic():
            for fecha, energia_total in tabla_energia.items():
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                MatrizEnergiaFlotaHistorico.objects.create(
                    bus=data['bus'],
                    dia=dia,
                    mes=mes,
                    año=año,
                    energia=round(energia_total, 2)
                )

    return "Datos de energía histórica guardados correctamente."


def scheduled_get_historical_data():
    # Obtener la fecha y hora actual en la zona horaria de Chile
    now = timezone.now().astimezone(pytz.timezone('America/Santiago'))
    dia = now.day
    mes = now.month
    año = now.year
    
    # Llama a la función para guardar los datos históricos de energía, pasando el día, mes y año
    save_historical_energy_data(dia, mes, año)


def iniciar_calculo_historico_diario(scheduler):
    # Configurar el trigger para que se ejecute todos los días a las 23:57 horas
    scheduler.add_job(
        scheduled_get_historical_data,
        trigger=CronTrigger(hour=11, minute=5, timezone=pytz.timezone('America/Santiago')),
        id="scheduled_get_historical_data",
        replace_existing=True,
    )
