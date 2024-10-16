from django.db import models
from bus_signals.models import Bus, Odometer

# Create your models here.

series_choices = (
    ('Queltehue', 'Queltehue'),
    ('Queltehue-Q2', 'Queltehue-Q2'),
    ('Tricahue', 'Tricahue'),
    ('Retrofit', 'Retrofit'),
)

class DisponibilidadFlota(models.Model):
  bus = models.CharField(max_length=50, blank=True, null=True)
  fecha = models.DateField(auto_now_add=True, blank=True, null=True)
  disponibilidad = models.BooleanField(default=True, blank=True, null=True)
  serie = models.CharField(max_length=50, choices=series_choices, blank=True, null=True)
  observacion = models.TextField(blank=True, null=True)
  dias_operativos = models.IntegerField(blank=True, null=True)
  dias_fs = models.IntegerField(blank=True, null=True)

  @property
  def total_op(self):
      if self.dias_operativos is not None and self.dias_fs is not None:
          return self.dias_operativos - self.dias_fs
      else:
          return None

  

  def __str__(self):
    return f'{self.bus} - {self.fecha} - {self.disponibilidad} - {self.serie}'
  
  class Meta:
    verbose_name = 'Disponibilidad de Flota'
    verbose_name_plural = 'Disponibilidad de Flota'
   
class Prueba(models.Model):
  valor = models.IntegerField()

  def __str__(self):
    return f'{self.valor}'
  
  class Meta:
    verbose_name = 'Prueba'
    verbose_name_plural = 'Prueba'

class MatrizKmFlotaHistorico(models.Model):
   bus = models.ForeignKey(Bus, on_delete=models.CASCADE, default=0)
   dia = models.IntegerField(null=True, blank=True)  # Cambiado a IntegerField para representar días
   mes = models.IntegerField(null=True, blank=True)  # Cambiado a IntegerField para facilitar la consulta
   año = models.IntegerField(null=True, blank=True)
   km_value = models.IntegerField(blank=True, null=True)

   def __str__(self):
    return f'{self.bus.bus_name} - {self.dia} - {self.mes} - {self.año} - {self.km_value}'
  
   class Meta:
    verbose_name = 'Informe Historico KM Flota'
    verbose_name_plural = 'Informes Historico KM Flota'

    
 

