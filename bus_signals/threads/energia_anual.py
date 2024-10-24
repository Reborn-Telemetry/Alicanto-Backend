from datetime import datetime
from reports.models import MatrizEnergiaFlotaHistorico
from bus_signals.models import AnualEnergy
from django.db.models import Sum
import logging

def calcular_energia_anual(year):
    # Filtrar los registros por el año específico y sumar los valores de energía
    total_energy = MatrizEnergiaFlotaHistorico.objects.filter(año=year).aggregate(total=Sum('energia'))['total']
    
    # Si no hay resultados, devolver 0 en lugar de None
    if total_energy is None:
        total_energy = 0
    
    return total_energy

def calcular_energia_anual_diaria():
    # Obtener el año actual
    year = datetime.now().year
    # Llamar a la función con el año actual
    total_energy = calcular_energia_anual(year)

    # Guardar la energía calculada en el modelo AnualEnergy
    AnualEnergy.objects.create(energia=total_energy)

    # Log para verificar la ejecución
    logging.info(f"Energía total calculada para el año {year}: {total_energy}")
