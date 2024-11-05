from django.db import models, transaction
from reports.models import Recorrido, DailyMatrizKmAutoReport, MatrizEnergiaFlotaHistorico

def remove_duplicates(model, unique_fields):
    """
    Elimina registros duplicados en el modelo especificado.
    Se mantiene el registro con el ID más alto (presumiblemente el más reciente).
    
    :param model: El modelo Django del cual eliminar duplicados.
    :param unique_fields: Lista de campos que definen un registro único.
    """
    duplicates = (
        model.objects.values(*unique_fields)
        .annotate(max_id=models.Max('id'), count=models.Count('id'))
        .filter(count__gt=1)
    )
    
    for entry in duplicates:
        with transaction.atomic():
            # Elimina todos los duplicados excepto el más reciente (max_id)
            model.objects.filter(**{field: entry[field] for field in unique_fields}) \
                .exclude(id=entry['max_id']).delete()

def eliminar_duplicados_diarios():
    """
    Ejecuta la eliminación de duplicados diariamente en los modelos `Recorrido`, 
    `DailyMatrizKmAutoReport` y `MatrizEnergiaFlotaHistorico`.
    """
    # Elimina duplicados en Recorrido basados en bus, dia, mes y año
    remove_duplicates(Recorrido, unique_fields=['bus', 'dia', 'mes', 'año'])

    # Elimina duplicados en DailyMatrizKmAutoReport basados en bus, dia, mes y año
    remove_duplicates(DailyMatrizKmAutoReport, unique_fields=['bus', 'dia', 'mes', 'año'])

    # Elimina duplicados en MatrizEnergiaFlotaHistorico basados en bus, dia, mes y año
    remove_duplicates(MatrizEnergiaFlotaHistorico, unique_fields=['bus', 'dia', 'mes', 'año'])
