from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Turno, ConfiguracionTurnos
from atracciones.models import Atraccion
from notificaciones.sms import enviar_sms


@login_required
def panel_admin(request):
    atracciones = Atraccion.objects.all().order_by('nombre')
    data = []
    for a in atracciones:
        en_fila = Turno.objects.filter(
            atraccion=a,
            estado__in=['generado', 'en_espera', 'proximo']
        ).count()
        data.append({'atraccion': a, 'en_fila': en_fila})
    return render(request, 'turnos/panel_admin.html', {'data': data})


@login_required
def panel_operador(request):
    atracciones = Atraccion.objects.filter(estado='abierta').order_by('nombre')
    data = []
    for a in atracciones:
        en_fila = Turno.objects.filter(
            atraccion=a,
            estado__in=['generado', 'en_espera', 'proximo']
        ).count()
        data.append({'atraccion': a, 'en_fila': en_fila})
    return render(request, 'turnos/panel_operador.html', {'data': data})


@login_required
def gestionar_cola(request, pk):
    atraccion = get_object_or_404(Atraccion, pk=pk)
    turnos = Turno.objects.filter(
        atraccion=atraccion,
        estado__in=['generado', 'en_espera', 'proximo', 'llamado']
    ).order_by('prioridad', 'numero')
    return render(request, 'turnos/gestionar_cola.html', {
        'atraccion': atraccion,
        'turnos': turnos,
    })


@login_required
def llamar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        turno.estado = 'llamado'
        if hasattr(turno, 'hora_llamado'):
            turno.hora_llamado = timezone.now()
        turno.save()

        # SMS al visitante cuando su turno es llamado
        if turno.visitante and turno.visitante.celular:
            enviar_sms(
                turno.visitante.celular,
                f'📣 ¡Tu turno #{turno.numero} para {turno.atraccion.nombre} '
                f'está siendo llamado! Dirígete a la atracción ahora.'
            )

    return redirect('turnos:gestionar_cola', pk=turno.atraccion.pk)


@login_required
def cambiar_estado(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        estados_validos = ['usado', 'vencido', 'cancelado']
        if nuevo_estado in estados_validos:
            turno.estado = nuevo_estado
            turno.save()
    return redirect('turnos:gestionar_cola', pk=turno.atraccion.pk)