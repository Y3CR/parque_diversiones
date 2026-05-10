from django.contrib import admin
from .models import ReglaTurno, Turno

@admin.register(ReglaTurno)
class ReglaAdmin(admin.ModelAdmin):
    list_display = ['atraccion', 'max_turnos_por_visitante', 'ventana_llamado_minutos']

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'atraccion', 'visitante', 'estado', 'hora_creacion', 'hora_estimada']
    list_filter = ['estado', 'atraccion']