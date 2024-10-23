from django.contrib import admin

from .models import DisponibilidadFlota, MatrizEnergiaFlotaHistorico, DailyMatrizKmAutoReport
admin.site.register(DisponibilidadFlota)
admin.site.register(MatrizEnergiaFlotaHistorico)
admin.site.register(DailyMatrizKmAutoReport)

# Register your models here.
