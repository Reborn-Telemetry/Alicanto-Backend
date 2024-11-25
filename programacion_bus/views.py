from django.shortcuts import render
from bus_signals.models import Bus
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . models import Programacion
# Create your views here.

def programacion(request):
  buses = Bus.bus.all()
  context = {
    'buses': buses,
  }

  return render(request,'pages/programacion.html', context )

@csrf_exempt
def guardar_programacion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        programacion = data.get('programacion', [])

        # Limpiar las asignaciones existentes antes de guardar las nuevas
        Programacion.objects.all().delete()

        # Guardar la nueva programación
        for item in programacion:
            bus_id = item.get('bus_id')
            turno = item.get('turno')
            if bus_id and turno:
                bus = Bus.bus.get(id=bus_id)
                Programacion.objects.create(bus=bus, turno=turno)

        return JsonResponse({'message': 'Programación guardada correctamente'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)