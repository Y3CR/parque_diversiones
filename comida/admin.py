from django.contrib import admin
from .models import Combo, Pedido, ItemPedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'precio', 'disponible']
    list_filter   = ['disponible']
    search_fields = ['nombre']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display  = ['codigo', 'visitante', 'estado', 'total', 'creado_en']
    list_filter   = ['estado']
    search_fields = ['codigo', 'visitante__nombre', 'visitante__celular']
    readonly_fields = ['codigo', 'creado_en']
    inlines       = [ItemPedidoInline]