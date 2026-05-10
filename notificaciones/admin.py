from django.contrib import admin
from .models import HistorialSMS

@admin.register(HistorialSMS)
class HistorialSMSAdmin(admin.ModelAdmin):
    list_display = ['visitante', 'celular', 'tipo_evento', 'estado_entrega', 'fecha_envio']
    list_filter = ['tipo_evento', 'estado_entrega']