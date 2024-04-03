from django.db import models

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
    
 

