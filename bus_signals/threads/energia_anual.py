import threading
import pytz
from datetime import datetime

from requests import request
from bus_signals.models import Bus, ChargeStatus, AnualEnergy

# Variable global para controlar si el cálculo ya está corriendo


def calcular_energia_anual():
    try:
        
        energia_anual = 0
        for i in Bus.bus.all():
            charge_data = ChargeStatus.charge_status.filter(bus_id=i.id).order_by('TimeStamp')

            rangos = []
            rango_actual = []

            for item in charge_data:
                if item.charge_status_value == 1:
                    rango_actual.append(item)
                elif item.charge_status_value == 0:
                    if rango_actual:
                        rangos.append(rango_actual.copy())
                        rango_actual.clear()

            if rango_actual:
                rangos.append(rango_actual)

            santiago_tz = pytz.timezone('Chile/Continental')

            datos_tabla = []
            for i, rango in enumerate(rangos, 1):
                fecha_inicio = rango[0].TimeStamp.strftime("%Y-%m-%d %H:%M:%S")
                fecha_termino = rango[-1].TimeStamp.strftime("%Y-%m-%d %H:%M:%S")
                soc_inicial = rango[0].soc_level
                soc_final = rango[-1].soc_level
                carga = soc_final - soc_inicial

                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S')
                fecha_termino_dt = datetime.strptime(fecha_termino, '%Y-%m-%d %H:%M:%S')

                fecha_inicio_dt_santiago = fecha_inicio_dt.replace(tzinfo=pytz.utc).astimezone(santiago_tz)
                fecha_termino_dt_santiago = fecha_termino_dt.replace(tzinfo=pytz.utc).astimezone(santiago_tz)

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
                })

            acu = round(sum(i['energia'] for i in datos_tabla), 2)
            energia_anual += acu
            energia_anual = round(energia_anual)
        AnualEnergy.objects.create(energia=energia_anual)

       

    except Exception as e:
        print(f"Error en el hilo: {e}")

# Llamada desde una función o vista
def iniciar_calculo():
    thread = threading.Thread(target=calcular_energia_anual, daemon=True)
    thread.start()
    
