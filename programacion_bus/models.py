from django.db import models
from bus_signals.models import Bus

# Create your models here.
class Programacion(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)  # Campo para la fecha de creación
    turno = models.CharField(
        max_length=50,
        choices=[
            ('turno-a', 'Turno A'),
            ('turno-b', 'Turno B'),
            ('turno-c', 'Turno C'),
            ('fs', 'FS')
        ]
    )