from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from atracciones.models import Atraccion
from turnos.models import Turno
from usuarios.models import Visitante
from notificaciones.sms import enviar_sms


def inicio(request):
    if request.method == 'POST':
        celular = request.POST.get('celular', '').strip()
        if celular:
            visitante, _ = Visitante.objects.get_or_create(
                celular=celular,
                defaults={'nombre': f'Visitante {celular[-4:]}'}
            )
            request.session['visitante_id'] = visitante.pk
            return redirect('portal:atracciones')
        messages.error(request, 'Ingresa un número de celular válido.')
    return render(request, 'portal/inicio.html')


def atracciones(request):
    visitante_id = request.session.get('visitante_id')
    if not visitante_id:
        return redirect('portal:inicio')
    visitante = get_object_or_404(Visitante, pk=visitante_id)
    atracciones = Atraccion.objects.filter(estado='abierta')
    return render(request, 'portal/atracciones.html', {
        'visitante': visitante,
        'atracciones': atracciones,
    })


def tomar_turno(request, pk):
    visitante_id = request.session.get('visitante_id')
    if not visitante_id:
        return redirect('portal:inicio')
    visitante = get_object_or_404(Visitante, pk=visitante_id)
    atraccion = get_object_or_404(Atraccion, pk=pk, estado='abierta')

    if request.method == 'POST':
        ya_tiene = Turno.objects.filter(
            visitante=visitante,
            atraccion=atraccion,
            estado__in=['generado', 'llamado']
        ).exists()
        if ya_tiene:
            messages.warning(request, 'Ya tienes un turno activo en esta atracción.')
        else:
            ultimo = Turno.objects.filter(atraccion=atraccion).order_by('-numero').first()
            nuevo_numero = (ultimo.numero + 1) if ultimo else 1
            turno = Turno.objects.create(
                atraccion=atraccion,
                visitante=visitante,
                numero=nuevo_numero,
                estado='generado',
                prioridad=0
            )
            messages.success(request, f'¡Turno #{nuevo_numero} generado para {atraccion.nombre}!')

            # SMS al tomar turno
            if visitante.celular:
                enviar_sms(
                    visitante.celular,
                    f'🎢 Turno #{turno.numero} confirmado para {atraccion.nombre}. '
                    f'Te avisaremos cuando sea tu momento. ¡Disfruta el parque!'
                )

        return redirect('portal:mis_turnos')
    return render(request, 'portal/atracciones.html', {'visitante': visitante, 'atraccion': atraccion})


def mis_turnos(request):
    visitante_id = request.session.get('visitante_id')
    if not visitante_id:
        return redirect('portal:inicio')
    visitante = get_object_or_404(Visitante, pk=visitante_id)
    turnos = Turno.objects.filter(
        visitante=visitante,
        estado__in=['generado', 'llamado']
    ).select_related('atraccion').order_by('-fecha_creacion')
    return render(request, 'portal/mis_turnos.html', {
        'visitante': visitante,
        'turnos': turnos,
    })


def salir(request):
    request.session.flush()
    return redirect('portal:inicio')