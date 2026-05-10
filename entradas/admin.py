from django.contrib import admin
from .models import TipoEntrada, Precio, Promocion, Entrada, AuditoriaAnulacion

@admin.register(TipoEntrada)
class TipoEntradaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']

@admin.register(Precio)
class PrecioAdmin(admin.ModelAdmin):
    list_display = ['tipo_entrada', 'valor', 'canal', 'vigencia_desde', 'vigencia_hasta']

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_entrada', 'descuento_porcentaje', 'vigencia_desde', 'vigencia_hasta', 'activa']

@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = ['visitante', 'tipo_entrada', 'precio_pagado', 'estado', 'canal_venta', 'fecha_compra']
    list_filter = ['estado', 'canal_venta']
    search_fields = ['visitante__nombre', 'visitante__celular']

@admin.register(AuditoriaAnulacion)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ['elemento_tipo', 'elemento_id', 'usuario', 'motivo', 'fecha']