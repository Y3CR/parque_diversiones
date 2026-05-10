from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Atraccion, CategoriaAtraccion, ESTADO_ATRACCION
from usuarios.decoradores import login_requerido, rol_requerido


@login_requerido
@rol_requerido('administrador')
def lista_atracciones(request):
    atracciones = Atraccion.objects.select_related('categoria').order_by('nombre')
    categorias = CategoriaAtraccion.objects.all()
    categoria_filtro = request.GET.get('categoria', '')
    estado_filtro = request.GET.get('estado', '')
    if categoria_filtro:
        atracciones = atracciones.filter(categoria_id=categoria_filtro)
    if estado_filtro:
        atracciones = atracciones.filter(estado=estado_filtro)
    return render(request, 'atracciones/lista.html', {
        'atracciones': atracciones,
        'categorias': categorias,
        'estados': ESTADO_ATRACCION,
        'categoria_filtro': categoria_filtro,
        'estado_filtro': estado_filtro,
    })


@login_requerido
@rol_requerido('administrador')
def crear_atraccion(request):
    categorias = CategoriaAtraccion.objects.all()
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        atraccion = Atraccion(
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion', ''),
            categoria_id=categoria_id if categoria_id else None,
            capacidad_por_ciclo=int(request.POST.get('capacidad_por_ciclo', 10)),
            duracion_promedio=int(request.POST.get('duracion_promedio', 5)),
            ubicacion=request.POST.get('ubicacion', ''),
            estado=request.POST.get('estado', 'abierta'),
            edad_minima=request.POST.get('edad_minima') or None,
            estatura_minima=request.POST.get('estatura_minima') or None,
            restricciones=request.POST.get('restricciones', ''),
            horario_apertura=request.POST.get('horario_apertura') or None,
            horario_cierre=request.POST.get('horario_cierre') or None,
            activa='activa' in request.POST,
        )
        if 'imagen' in request.FILES:
            atraccion.imagen = request.FILES['imagen']
        atraccion.save()
        messages.success(request, f'Atracción "{atraccion.nombre}" creada correctamente.')
        return redirect('atracciones:lista')
    return render(request, 'atracciones/form_atraccion.html', {
        'categorias': categorias,
        'estados': ESTADO_ATRACCION,
    })


@login_requerido
@rol_requerido('administrador')
def editar_atraccion(request, pk):
    atraccion = get_object_or_404(Atraccion, pk=pk)
    categorias = CategoriaAtraccion.objects.all()
    if request.method == 'POST':
        atraccion.nombre = request.POST.get('nombre')
        atraccion.descripcion = request.POST.get('descripcion', '')
        categoria_id = request.POST.get('categoria')
        atraccion.categoria_id = categoria_id if categoria_id else None
        atraccion.capacidad_por_ciclo = int(request.POST.get('capacidad_por_ciclo', 10))
        atraccion.duracion_promedio = int(request.POST.get('duracion_promedio', 5))
        atraccion.ubicacion = request.POST.get('ubicacion', '')
        atraccion.estado = request.POST.get('estado', 'abierta')
        atraccion.edad_minima = request.POST.get('edad_minima') or None
        atraccion.estatura_minima = request.POST.get('estatura_minima') or None
        atraccion.restricciones = request.POST.get('restricciones', '')
        atraccion.horario_apertura = request.POST.get('horario_apertura') or None
        atraccion.horario_cierre = request.POST.get('horario_cierre') or None
        atraccion.activa = 'activa' in request.POST
        if 'imagen' in request.FILES:
            atraccion.imagen = request.FILES['imagen']
        atraccion.save()
        messages.success(request, f'Atracción "{atraccion.nombre}" actualizada.')
        return redirect('atracciones:lista')
    return render(request, 'atracciones/form_atraccion.html', {
        'object': atraccion,
        'categorias': categorias,
        'estados': ESTADO_ATRACCION,
    })


@login_requerido
@rol_requerido('administrador', 'operador_atraccion')
def cambiar_estado(request, pk):
    atraccion = get_object_or_404(Atraccion, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        estado_anterior = atraccion.estado
        atraccion.estado = nuevo_estado
        atraccion.save()

        # Si se cierra, cancelar turnos activos
        if nuevo_estado in ['cerrada', 'mantenimiento', 'suspendida']:
            from turnos.models import Turno
            turnos_afectados = Turno.objects.filter(
                atraccion=atraccion,
                estado__in=['generado', 'en_espera', 'proximo']
            )
            count = turnos_afectados.count()
            turnos_afectados.update(estado='cancelado')
            if count:
                messages.warning(
                    request,
                    f'{count} turno(s) cancelados porque la atracción cambió a {atraccion.get_estado_display()}.'
                )

        messages.success(
            request,
            f'Estado cambiado de "{dict(ESTADO_ATRACCION)[estado_anterior]}" '
            f'a "{atraccion.get_estado_display()}".'
        )
        return redirect('atracciones:lista')
    return render(request, 'atracciones/cambiar_estado.html', {
        'atraccion': atraccion,
        'estados': ESTADO_ATRACCION,
    })


@login_requerido
@rol_requerido('administrador')
def toggle_activa(request, pk):
    atraccion = get_object_or_404(Atraccion, pk=pk)
    atraccion.activa = not atraccion.activa
    atraccion.save()
    estado_txt = 'activada' if atraccion.activa else 'desactivada'
    messages.success(request, f'Atracción "{atraccion.nombre}" {estado_txt}.')
    return redirect('atracciones:lista')


# ── Categorías ──────────────────────────────────────────────

@login_requerido
@rol_requerido('administrador')
def lista_categorias(request):
    categorias = CategoriaAtraccion.objects.all().order_by('nombre')
    return render(request, 'atracciones/lista_categorias.html', {'categorias': categorias})


@login_requerido
@rol_requerido('administrador')
def crear_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
        elif CategoriaAtraccion.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, 'Ya existe una categoría con ese nombre.')
        else:
            CategoriaAtraccion.objects.create(
                nombre=nombre,
                descripcion=request.POST.get('descripcion', '')
            )
            messages.success(request, f'Categoría "{nombre}" creada.')
            return redirect('atracciones:categorias')
    return render(request, 'atracciones/form_categoria.html')


@login_requerido
@rol_requerido('administrador')
def editar_categoria(request, pk):
    categoria = get_object_or_404(CategoriaAtraccion, pk=pk)
    if request.method == 'POST':
        categoria.nombre = request.POST.get('nombre', categoria.nombre).strip()
        categoria.descripcion = request.POST.get('descripcion', '')
        categoria.save()
        messages.success(request, 'Categoría actualizada.')
        return redirect('atracciones:categorias')
    return render(request, 'atracciones/form_categoria.html', {'object': categoria})