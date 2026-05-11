from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import TipoEntrada, Precio, Promocion, Entrada, AuditoriaAnulacion
from usuarios.models import Visitante
from usuarios.models import UsuarioInterno
from usuarios.decoradores import login_requerido, rol_requerido
import uuid


# ── Tipos de entrada ─────────────────────────────────────────

@login_requerido
@rol_requerido('administrador')
def lista_tipos(request):
    tipos = TipoEntrada.objects.all().order_by('nombre')
    return render(request, 'entradas/lista_tipos.html', {'tipos': tipos})


@login_requerido
@rol_requerido('administrador')
def crear_tipo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
        else:
            TipoEntrada.objects.create(
                nombre=nombre,
                descripcion=request.POST.get('descripcion', ''),
                activo='activo' in request.POST,
            )
            messages.success(request, f'Tipo "{nombre}" creado.')
            return redirect('entradas:tipos')
    return render(request, 'entradas/form_tipo.html')


@login_requerido
@rol_requerido('administrador')
def editar_tipo(request, pk):
    tipo = get_object_or_404(TipoEntrada, pk=pk)
    if request.method == 'POST':
        tipo.nombre = request.POST.get('nombre', tipo.nombre).strip()
        tipo.descripcion = request.POST.get('descripcion', '')
        tipo.activo = 'activo' in request.POST
        tipo.save()
        messages.success(request, 'Tipo actualizado.')
        return redirect('entradas:tipos')
    return render(request, 'entradas/form_tipo.html', {'object': tipo})


# ── Precios ──────────────────────────────────────────────────

@login_requerido
@rol_requerido('administrador')
def lista_precios(request):
    precios = Precio.objects.select_related('tipo_entrada', 'usuario_modifico').order_by(
        'tipo_entrada__nombre', '-vigencia_desde'
    )
    return render(request, 'entradas/lista_precios.html', {'precios': precios})


@login_requerido
@rol_requerido('administrador')
def crear_precio(request):
    tipos = TipoEntrada.objects.filter(activo=True)
    if request.method == 'POST':
        tipo_id = request.POST.get('tipo_entrada')
        tipo = get_object_or_404(TipoEntrada, pk=tipo_id)
        canal = request.POST.get('canal', 'web')
        nuevo_valor = request.POST.get('valor')

        # Guardar valor anterior para historial (HU-32)
        precio_anterior = Precio.objects.filter(
            tipo_entrada=tipo,
            canal=canal,
        ).order_by('-vigencia_desde').first()

        Precio.objects.create(
            tipo_entrada=tipo,
            valor=nuevo_valor,
            canal=canal,
            vigencia_desde=request.POST.get('vigencia_desde'),
            vigencia_hasta=request.POST.get('vigencia_hasta') or None,
            valor_anterior=precio_anterior.valor if precio_anterior else None,
            usuario_modifico=request.user,
        )
        messages.success(request, f'Precio creado para {tipo.nombre}. Historial conservado.')
        return redirect('entradas:precios')
    return render(request, 'entradas/form_precio.html', {'tipos': tipos})


# ── Promociones ──────────────────────────────────────────────

@login_requerido
@rol_requerido('administrador')
def lista_promociones(request):
    promociones = Promocion.objects.select_related('tipo_entrada').order_by('-vigencia_desde')
    return render(request, 'entradas/lista_promociones.html', {'promociones': promociones})


@login_requerido
@rol_requerido('administrador')
def crear_promocion(request):
    tipos = TipoEntrada.objects.filter(activo=True)
    if request.method == 'POST':
        Promocion.objects.create(
            nombre=request.POST.get('nombre'),
            tipo_entrada_id=request.POST.get('tipo_entrada'),
            descuento_porcentaje=request.POST.get('descuento_porcentaje'),
            vigencia_desde=request.POST.get('vigencia_desde'),
            vigencia_hasta=request.POST.get('vigencia_hasta'),
            canal=request.POST.get('canal', 'taquilla'),
            activa='activa' in request.POST,
        )
        messages.success(request, 'Promoción creada.')
        return redirect('entradas:promociones')
    return render(request, 'entradas/form_promocion.html', {'tipos': tipos})


@login_requerido
@rol_requerido('administrador')
def editar_promocion(request, pk):
    promo = get_object_or_404(Promocion, pk=pk)
    tipos = TipoEntrada.objects.filter(activo=True)
    if request.method == 'POST':
        promo.nombre = request.POST.get('nombre')
        promo.tipo_entrada_id = request.POST.get('tipo_entrada')
        promo.descuento_porcentaje = request.POST.get('descuento_porcentaje')
        promo.vigencia_desde = request.POST.get('vigencia_desde')
        promo.vigencia_hasta = request.POST.get('vigencia_hasta')
        promo.canal = request.POST.get('canal', 'taquilla')
        promo.activa = 'activa' in request.POST
        promo.save()
        messages.success(request, 'Promoción actualizada.')
        return redirect('entradas:promociones')
    return render(request, 'entradas/form_promocion.html', {
        'object': promo, 'tipos': tipos
    })


# ── Utilidad: precio vigente ─────────────────────────────────

def obtener_precio_vigente(tipo, canal):
    hoy = timezone.now().date()
    return Precio.objects.filter(
        tipo_entrada=tipo,
        canal=canal,
        vigencia_desde__lte=hoy,
    ).filter(
        Q(vigencia_hasta__isnull=True) | Q(vigencia_hasta__gte=hoy)
    ).order_by('-vigencia_desde').first()


def obtener_promocion_vigente(tipo, canal):
    hoy = timezone.now().date()
    return Promocion.objects.filter(
        tipo_entrada=tipo,
        canal=canal,
        activa=True,
        vigencia_desde__lte=hoy,
        vigencia_hasta__gte=hoy,
    ).first()


# ── Venta en taquilla (HU-12, HU-14) ────────────────────────

@login_requerido
@rol_requerido('taquilla', 'administrador')
def vender_entrada(request):
    tipos = TipoEntrada.objects.filter(activo=True)
    precio_calculado = None
    tipo_sel = None
    promo_sel = None

    if request.method == 'GET' and request.GET.get('tipo'):
        tipo_sel = get_object_or_404(TipoEntrada, pk=request.GET.get('tipo'))
        precio_obj = obtener_precio_vigente(tipo_sel, 'taquilla')
        promo_sel = obtener_promocion_vigente(tipo_sel, 'taquilla')
        if precio_obj:
            valor = float(precio_obj.valor)
            if promo_sel:
                descuento = valor * float(promo_sel.descuento_porcentaje) / 100
                valor = round(valor - descuento, 2)
            precio_calculado = valor

    if request.method == 'POST':
        tipo = get_object_or_404(TipoEntrada, pk=request.POST.get('tipo_entrada'))
        nombre = request.POST.get('nombre_visitante', '').strip()
        celular = request.POST.get('celular', '').strip()

        if not nombre or not celular:
            messages.error(request, 'Nombre y celular del visitante son obligatorios.')
            return redirect('entradas:vender')

        visitante, _ = Visitante.objects.get_or_create(
            celular=celular,
            defaults={'nombre': nombre}
        )
        if not visitante.nombre:
            visitante.nombre = nombre
            visitante.save()

        precio_obj = obtener_precio_vigente(tipo, 'taquilla')
        if not precio_obj:
            messages.error(request, 'Este tipo de entrada no tiene precio configurado para taquilla.')
            return redirect('entradas:vender')

        valor = float(precio_obj.valor)
        promo = obtener_promocion_vigente(tipo, 'taquilla')
        if promo:
            descuento = valor * float(promo.descuento_porcentaje) / 100
            valor = round(valor - descuento, 2)

        entrada = Entrada.objects.create(
            visitante=visitante,
            tipo_entrada=tipo,
            precio_pagado=valor,
            canal_venta='taquilla',
            fecha_uso=timezone.now().date(),
            vendido_por=request.user,
            estado='activa',
        )
        messages.success(
            request,
            f'Entrada vendida. Código: {entrada.codigo_str()} | '
            f'Visitante: {visitante.nombre} | Valor: ${valor:,.0f}'
        )
        return redirect('entradas:detalle_entrada', pk=entrada.pk)

    return render(request, 'entradas/vender.html', {
        'tipos': tipos,
        'tipo_sel': tipo_sel,
        'precio_calculado': precio_calculado,
        'promo_sel': promo_sel,
    })


# ── Validar entrada (HU-13) ──────────────────────────────────

@login_requerido
@rol_requerido('taquilla', 'administrador')
def validar_entrada(request):
    entrada = None
    codigo = ''
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        # Buscar por UUID completo o por los primeros 10 caracteres
        try:
            entrada = Entrada.objects.select_related('visitante', 'tipo_entrada').get(
                codigo_validacion=codigo
            )
        except (Entrada.DoesNotExist, Exception):
            # Buscar por código corto
            todas = Entrada.objects.select_related('visitante', 'tipo_entrada').all()
            for e in todas:
                if e.codigo_str() == codigo[:10]:
                    entrada = e
                    break

        if not entrada:
            messages.error(request, f'No se encontró ninguna entrada con el código "{codigo}".')
        elif entrada.estado == 'usada':
            messages.warning(request, f'Esta entrada ya fue utilizada.')
        elif entrada.estado == 'anulada':
            messages.error(request, 'Esta entrada fue anulada.')
        elif entrada.estado == 'vencida':
            messages.error(request, 'Esta entrada está vencida.')
        else:
            if request.POST.get('confirmar_uso'):
                entrada.estado = 'usada'
                entrada.fecha_uso = timezone.now().date()
                entrada.save()
                messages.success(
                    request,
                    f'✅ Entrada validada. Visitante: {entrada.visitante.nombre}'
                )
                entrada = None
                codigo = ''
            else:
                messages.info(request, 'Entrada válida. Confirma el ingreso.')

    return render(request, 'entradas/validar.html', {
        'entrada': entrada,
        'codigo': codigo,
    })


# ── Compra web (HU-03) ───────────────────────────────────────

def compra_web(request):
    tipos = TipoEntrada.objects.filter(activo=True)
    precios_por_tipo = {}
    for tipo in tipos:
        precio_obj = obtener_precio_vigente(tipo, 'web')
        promo = obtener_promocion_vigente(tipo, 'web')
        if precio_obj:
            valor = float(precio_obj.valor)
            if promo:
                descuento = valor * float(promo.descuento_porcentaje) / 100
                valor = round(valor - descuento, 2)
            precios_por_tipo[tipo.pk] = {
                'valor': valor,
                'original': float(precio_obj.valor),
                'promo': promo,
            }

    if request.method == 'POST':
        tipo = get_object_or_404(TipoEntrada, pk=request.POST.get('tipo_entrada'))
        nombre = request.POST.get('nombre', '').strip()
        celular = request.POST.get('celular', '').strip()
        correo = request.POST.get('correo', '').strip()

        if not nombre or not celular:
            messages.error(request, 'Nombre y celular son obligatorios.')
            return render(request, 'entradas/compra_web.html', {
                'tipos': tipos, 'precios': precios_por_tipo
            })

        visitante, _ = Visitante.objects.get_or_create(
            celular=celular,
            defaults={'nombre': nombre, 'correo': correo or None}
        )

        datos = precios_por_tipo.get(tipo.pk)
        if not datos:
            messages.error(request, 'Este tipo de entrada no está disponible en línea.')
            return render(request, 'entradas/compra_web.html', {
                'tipos': tipos, 'precios': precios_por_tipo
            })

        entrada = Entrada.objects.create(
            visitante=visitante,
            tipo_entrada=tipo,
            precio_pagado=datos['valor'],
            canal_venta='web',
            fecha_uso=timezone.now().date(),
            estado='activa',
        )
        return redirect('entradas:comprobante', pk=entrada.pk)

    return render(request, 'entradas/compra_web.html', {
        'tipos': tipos,
        'precios': precios_por_tipo,
    })


# ── Lista de entradas ─────────────────────────────────────────

@login_requerido
@rol_requerido('taquilla', 'administrador', 'soporte')
def lista_entradas(request):
    hoy = timezone.now().date()
    entradas = Entrada.objects.select_related(
        'visitante', 'tipo_entrada', 'vendido_por'
    ).filter(fecha_compra__date=hoy).order_by('-fecha_compra')

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        entradas = Entrada.objects.select_related(
            'visitante', 'tipo_entrada', 'vendido_por'
        ).filter(
            Q(visitante__nombre__icontains=busqueda) |
            Q(visitante__celular__icontains=busqueda)
        ).order_by('-fecha_compra')

    return render(request, 'entradas/lista_entradas.html', {
        'entradas': entradas,
        'busqueda': busqueda,
        'hoy': hoy,
    })


# ── Detalle y comprobante ─────────────────────────────────────

@login_requerido
@rol_requerido('taquilla', 'administrador', 'soporte')
def detalle_entrada(request, pk):
    entrada = get_object_or_404(
        Entrada.objects.select_related('visitante', 'tipo_entrada', 'vendido_por'),
        pk=pk
    )
    return render(request, 'entradas/detalle_entrada.html', {'entrada': entrada})


def comprobante(request, pk):
    entrada = get_object_or_404(
        Entrada.objects.select_related('visitante', 'tipo_entrada'),
        pk=pk
    )
    return render(request, 'entradas/comprobante.html', {'entrada': entrada})


# ── Anular entrada (HU-15, HU-33) ────────────────────────────

@login_requerido
@rol_requerido('taquilla', 'administrador')
def anular_entrada(request, pk):
    entrada = get_object_or_404(Entrada, pk=pk)
    if entrada.estado == 'anulada':
        messages.warning(request, 'Esta entrada ya estaba anulada.')
        return redirect('entradas:lista_entradas')

    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        if not motivo:
            messages.error(request, 'El motivo de anulación es obligatorio.')
            return render(request, 'entradas/anular.html', {'entrada': entrada})

        estado_anterior = entrada.estado
        entrada.estado = 'anulada'
        entrada.save()

        AuditoriaAnulacion.objects.create(
            elemento_tipo='entrada',
            elemento_id=entrada.pk,
            usuario=request.user,
            rol_usuario=request.user.rol,
            motivo=motivo,
            estado_anterior=estado_anterior,
        )
        messages.success(request, f'Entrada {entrada.codigo_str()} anulada. Registro guardado.')
        return redirect('entradas:lista_entradas')

    return render(request, 'entradas/anular.html', {'entrada': entrada})