from django.contrib import admin
from .models import CategoriaAtraccion, Atraccion

@admin.register(CategoriaAtraccion)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']

@admin.register(Atraccion)
class AtraccionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'estado', 'capacidad_por_ciclo', 'duracion_promedio', 'activa']
    list_filter = ['estado', 'categoria', 'activa']
    search_fields = ['nombre']
    list_editable = ['estado', 'activa']