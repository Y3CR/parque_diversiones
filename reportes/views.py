from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum
import csv
from datetime import date

from atracciones.models import Atraccion
from turnos.models import Turno
from usuarios.models import Visitante, PaseNitro
from entradas.models import Entrada
from comida.models import Pedido, ItemPedido


@login_required
def dashboard(request):
    hoy = date.today()

    # KPIs principales
    visitantes_hoy   = Visitante.objects.filter(fecha_registro__date=hoy).count()
    turnos_activos   = Turno.objects.filter(estado__in=['generado', 'llamado']).count()
    pedidos_activos  = Pedido.objects.exclude(estado__in=['entregado', 'cancelado']).count()
    entradas_hoy     = Entrada.objects.filter(fecha_compra__date=hoy).count() if hasattr(Entrada, 'fecha_compra') else 0

    # Atracciones
    atracciones_abiertas  = Atraccion.objects.filter(estado='abierta').count()
    atracciones_cerradas  = Atraccion.objects.exclude(estado='abierta').count()

    # Cola por atracción
    cola_por_atraccion = Turno.objects.filter(
        estado__in=['generado', 'llamado']
    ).values('atraccion__nombre').annotate(total=Count('id')).order_by('-total')

    # Pedidos por estado
    pedidos_por_estado = Pedido.objects.values('estado').annotate(total=Count('id'))

    # Pases Nitro activos hoy
    nitros_activos = PaseNitro.objects.filter(activo=True, fecha_fin__gte=hoy).count()

    return render(request, 'reportes/dashboard.html', {
        'visitantes_hoy':      visitantes_hoy,
        'turnos_activos':      turnos_activos,
        'pedidos_activos':     pedidos_activos,
        'entradas_hoy':        entradas_hoy,
        'atracciones_abiertas': atracciones_abiertas,
        'atracciones_cerradas': atracciones_cerradas,
        'cola_por_atraccion':  cola_por_atraccion,
        'pedidos_por_estado':  pedidos_por_estado,
        'nitros_activos':      nitros_activos,
        'hoy':                 hoy,
    })


@login_required
def reporte_turnos(request):
    turnos = Turno.objects.values(
        'atraccion__nombre', 'estado'
    ).annotate(total=Count('id')).order_by('atraccion__nombre', 'estado')
    return render(request, 'reportes/reporte_turnos.html', {'turnos': turnos})


@login_required
def reporte_comida(request):
    items = ItemPedido.objects.values(
        'combo__nombre'
    ).annotate(
        total_vendidos=Sum('cantidad'),
        total_ingresos=Sum('subtotal')
    ).order_by('-total_vendidos')
    return render(request, 'reportes/reporte_comida.html', {'items': items})


@login_required
def exportar_turnos_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="turnos.csv"'
    writer = csv.writer(response)
    writer.writerow(['Atracción', 'Estado', 'Total'])
    datos = Turno.objects.values(
        'atraccion__nombre', 'estado'
    ).annotate(total=Count('id')).order_by('atraccion__nombre')
    for row in datos:
        writer.writerow([row['atraccion__nombre'], row['estado'], row['total']])
    return response


@login_required
def exportar_comida_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pedidos_comida.csv"'
    writer = csv.writer(response)
    writer.writerow(['Combo', 'Cantidad vendida', 'Ingresos'])
    datos = ItemPedido.objects.values('combo__nombre').annotate(
        total=Sum('cantidad'), ingresos=Sum('subtotal')
    ).order_by('-total')
    for row in datos:
        writer.writerow([row['combo__nombre'], row['total'], row['ingresos']])
    return response