from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from atracciones.models import Atraccion
from turnos.models import Turno
from usuarios.models import Visitante, PaseNitro
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
    nitro_activo = PaseNitro.objects.filter(
        visitante=visitante, activo=True,
        fecha_fin__gte=timezone.now().date(),
        usos_restantes__gt=0
    ).first()
    return render(request, 'portal/atracciones.html', {
        'visitante': visitante,
        'atracciones': atracciones,
        'nitro_activo': nitro_activo,
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

            # Verificar si tiene Nitro activo y la atracción lo acepta
            prioridad = 0
            nitro_usado = None
            if atraccion.acepta_nitro:
                nitro = PaseNitro.objects.filter(
                    visitante=visitante, activo=True,
                    fecha_fin__gte=timezone.now().date(),
                    usos_restantes__gt=0
                ).first()
                if nitro:
                    prioridad = 1
                    nitro.usos_restantes -= 1
                    if nitro.usos_restantes == 0:
                        nitro.activo = False
                    nitro.save()
                    nitro_usado = nitro

            turno = Turno.objects.create(
                atraccion=atraccion,
                visitante=visitante,
                numero=nuevo_numero,
                estado='generado',
                prioridad=prioridad
            )

            if nitro_usado:
                messages.success(request, f'⚡ Turno Nitro #{turno.numero} generado para {atraccion.nombre}! '
                                          f'(Usos restantes: {nitro_usado.usos_restantes})')
            else:
                messages.success(request, f'¡Turno #{turno.numero} generado para {atraccion.nombre}!')

            if visitante.celular:
                tipo_turno = '⚡ Nitro' if nitro_usado else 'normal'
                enviar_sms(
                    visitante.celular,
                    f'🎢 Turno {tipo_turno} #{turno.numero} confirmado para {atraccion.nombre}. '
                    f'Te avisaremos cuando sea tu momento.'
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
    nitro_activo = PaseNitro.objects.filter(
        visitante=visitante, activo=True,
        fecha_fin__gte=timezone.now().date(),
        usos_restantes__gt=0
    ).first()
    return render(request, 'portal/mis_turnos.html', {
        'visitante': visitante,
        'turnos': turnos,
        'nitro_activo': nitro_activo,
    })


def comprar_nitro(request):
    visitante_id = request.session.get('visitante_id')
    if not visitante_id:
        return redirect('portal:inicio')
    visitante = get_object_or_404(Visitante, pk=visitante_id)

    if request.method == 'POST':
        tipo = request.POST.get('tipo', 'por_usos')
        PaseNitro.objects.create(
            visitante=visitante,
            tipo=tipo,
            usos_totales=3,
            usos_restantes=3,
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date(),  # mismo día
            activo=True,
            creado_por='portal'
        )
        messages.success(request, '⚡ ¡Pase Nitro activado! Tienes 3 usos para hoy.')
        return redirect('portal:mis_turnos')

    return render(request, 'portal/comprar_nitro.html')


def salir(request):
    request.session.flush()
    return redirect('portal:inicio')