import threading
import pytz
from pytz import timezone
from datetime import datetime
from requests import request
from bus_signals.models import Bus, ChargeStatus, AnualEnergy
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.triggers.cron import CronTrigger
from reports.models import MatrizEnergiaFlotaHistorico
from django.db.models import Q, Count, Sum, Max, F, Avg
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from apscheduler.schedulers.background import BackgroundScheduler


def calcular_energia_anual(year):
    # Filtrar los registros por el año específico y sumar los valores de energía
    total_energy = MatrizEnergiaFlotaHistorico.objects.filter(año=year).aggregate(total=Sum('energia'))['total']
    
    # Si no hay resultados, devolver 0 en lugar de None
    if total_energy is None:
        total_energy = 0
    
    return total_energy


# Esta es la función que se ejecutará diariamente
def calcular_energia_anual_diaria():
    year = datetime.now().year  # Obtener el año actual
    calcular_energia_anual(year)  # Llamar a la función con el año actual


def iniciar_calculo_diario():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Configurar el trigger para que se ejecute todos los días a las 11 AM hora de Chile
    scheduler.add_job(
        'bus_signals.threads.energia_anual:calcular_energia_anual_diaria',
        trigger=CronTrigger(hour=10, minute=0, timezone=timezone("America/Santiago")),  # 11:00 AM Chile
        id="calcular_energia_anual_diaria",
        replace_existing=True,
    )

    scheduler.start()