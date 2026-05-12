from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Combo, Pedido, ItemPedido
from usuarios.models import Visitante
from notificaciones.sms import enviar_sms


# ── Portal del visitante ──────────────────────────────────────

def catalogo(request):
    visitante_id = request.session.get('visitante_id')
    if not visitante_id:
        return redirect('portal:inicio')
    visitante = get_object_or_404(Visitante, pk=visitante_id)
    combos = Combo.objects.filter(disponible=True)
    return render(request, 'comida/catalogo.html', {
        'visitante': visitante,
        'combos': combos,
    })


def hacer_pedido(request, pk):
    visitante_id = request.session.get('visitante_id')
    if not visitante_id:
        return redirect('portal:inicio')
    visitante = get_object_or_404(Visitante, pk=visitante_id)
    combo = get_object_or_404(Combo, pk=pk, disponible=True)

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        pedido = Pedido.objects.create(
            visitante=visitante,
            estado='recibido',
            total=combo.precio * cantidad
        )
        ItemPedido.objects.create(
            pedido=pedido,
            combo=combo,
            cantidad=cantidad
        )
        messages.success(request, f'✅ Pedido #{pedido.codigo} recibido. Te avisamos cuando esté listo.')
        if visitante.celular:
            enviar_sms(
                visitante.celular,
                f'🍔 Pedido #{pedido.codigo} recibido: {cantidad}x {combo.nombre}. '
                f'Te avisaremos cuando esté listo para recoger.'
            )
        return redirect('comida:mis_pedidos')

    return render(request, 'comida/hacer_pedido.html', {
        'visitante': visitante,
        'combo': combo,
    })


def mis_pedidos(request):
    visitante_id = request.session.get('visitante_id')
    if not visitante_id:
        return redirect('portal:inicio')
    visitante = get_object_or_404(Visitante, pk=visitante_id)
    pedidos = Pedido.objects.filter(visitante=visitante).order_by('-creado_en')
    return render(request, 'comida/mis_pedidos.html', {
        'visitante': visitante,
        'pedidos': pedidos,
    })


# ── Panel operador de alimentos ───────────────────────────────

@login_required
def panel_alimentos(request):
    pedidos = Pedido.objects.exclude(
        estado__in=['entregado', 'cancelado']
    ).order_by('creado_en')
    return render(request, 'comida/panel_alimentos.html', {'pedidos': pedidos})


@login_required
def cambiar_estado_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        estados_validos = ['preparacion', 'listo', 'entregado', 'cancelado']
        if nuevo_estado in estados_validos:
            pedido.estado = nuevo_estado
            pedido.save()
            # SMS cuando el pedido está listo
            if nuevo_estado == 'listo' and pedido.visitante.celular:
                enviar_sms(
                    pedido.visitante.celular,
                    f'🍔 ¡Tu pedido #{pedido.codigo} está listo! '
                    f'Recógelo en el punto de alimentos.'
                )
            messages.success(request, f'Pedido {pedido.codigo} actualizado a {pedido.get_estado_display()}.')
    return redirect('comida:panel_alimentos')