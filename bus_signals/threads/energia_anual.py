from pytz import timezone
from datetime import datetime
from reports.models import MatrizEnergiaFlotaHistorico
from bus_signals.models import AnualEnergy  # Asegúrate de importar tu modelo AnualEnergy
from django.db.models import Sum
from apscheduler.triggers.cron import CronTrigger
import logging


def calcular_energia_anual(year):
    # Filtrar los registros por el año específico y sumar los valores de energía
    total_energy = MatrizEnergiaFlotaHistorico.objects.filter(año=year).aggregate(total=Sum('energia'))['total']
    
    # Si no hay resultados, devolver 0 en lugar de None
    if total_energy is None:
        total_energy = 0
    
    return total_energy


# Esta es la función que se ejecutará diariamente
def calcular_energia_anual_diaria():
    # Obtener el año actual
    year = datetime.now().year
    # Llamar a la función con el año actual
    total_energy = calcular_energia_anual(year)

    # Guardar la energía calculada en el modelo AnualEnergy
    AnualEnergy.objects.create(energia=total_energy)

    # Log para verificar la ejecución
    logging.info(f"Energía total calculada para el año {year}: {total_energy}")


def iniciar_calculo_diario(scheduler):
    # Configurar el trigger para que se ejecute todos los días a las 12:30 PM hora de Chile
    scheduler.add_job(
        calcular_energia_anual_diaria,  # La función que se ejecutará diariamente
        trigger=CronTrigger(hour=12, minute=40, timezone=timezone("America/Santiago")),
        id="calcular_energia_anual_diaria",
        replace_existing=True,
    )
