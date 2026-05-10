from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from .models import UsuarioInterno, Visitante, ROL_CHOICES
from .decoradores import login_requerido, rol_requerido


def vista_login(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.activo:
            login(request, user)
            return redirect('usuarios:dashboard')
        messages.error(request, 'Credenciales incorrectas o usuario inactivo.')
    return render(request, 'usuarios/login.html')


def vista_logout(request):
    logout(request)
    return redirect('usuarios:login')


@login_requerido
def dashboard(request):
    from atracciones.models import Atraccion
    from entradas.models import Entrada
    from turnos.models import Turno

    hoy = timezone.now().date()
    context = {
        'total_atracciones': Atraccion.objects.filter(activa=True).count(),
        'entradas_hoy': Entrada.objects.filter(fecha_compra__date=hoy).count(),
        'turnos_activos': Turno.objects.filter(
            estado__in=['generado', 'en_espera', 'proximo']
        ).count(),
        'visitantes_hoy': Entrada.objects.filter(
            fecha_compra__date=hoy
        ).values('visitante').distinct().count(),
    }
    return render(request, 'usuarios/dashboard.html', context)


@login_requerido
@rol_requerido('administrador')
def lista_usuarios(request):
    usuarios = UsuarioInterno.objects.all().order_by('rol', 'first_name')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


@login_requerido
@rol_requerido('administrador')
def crear_usuario(request):
    if request.method == 'POST':
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        if p1 != p2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'usuarios/form_usuario.html', {'roles': ROL_CHOICES})
        if UsuarioInterno.objects.filter(username=request.POST.get('username')).exists():
            messages.error(request, 'Ese nombre de usuario ya existe.')
            return render(request, 'usuarios/form_usuario.html', {'roles': ROL_CHOICES})
        user = UsuarioInterno.objects.create_user(
            username=request.POST.get('username'),
            password=p1,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            email=request.POST.get('email', ''),
            rol=request.POST.get('rol', 'taquilla'),
            activo='activo' in request.POST,
        )
        messages.success(request, f'Usuario {user.username} creado correctamente.')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/form_usuario.html', {'roles': ROL_CHOICES})


@login_requerido
@rol_requerido('administrador')
def editar_usuario(request, pk):
    usuario = get_object_or_404(UsuarioInterno, pk=pk)
    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name', '')
        usuario.last_name  = request.POST.get('last_name', '')
        usuario.email      = request.POST.get('email', '')
        usuario.rol        = request.POST.get('rol', usuario.rol)
        usuario.activo     = 'activo' in request.POST
        usuario.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/form_usuario.html', {
        'object': usuario,
        'roles': ROL_CHOICES,
    })


@login_requerido
@rol_requerido('soporte', 'administrador')
def buscar_visitante(request):
    visitante = None
    entradas  = []
    turnos    = []
    query     = request.GET.get('q', '').strip()
    if query:
        from entradas.models import Entrada
        from turnos.models import Turno
        visitante = (
            Visitante.objects.filter(celular__icontains=query).first()
            or Visitante.objects.filter(correo__icontains=query).first()
        )
        if visitante:
            entradas = visitante.entradas.all().order_by('-fecha_compra')[:10]
            turnos   = visitante.turnos.all().order_by('-hora_creacion')[:10]
    return render(request, 'usuarios/buscar_visitante.html', {
        'visitante': visitante,
        'entradas':  entradas,
        'turnos':    turnos,
        'query':     query,
    })