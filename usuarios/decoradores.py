from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def rol_requerido(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.rol not in roles:
                messages.error(request, 'No tienes permiso para acceder a esta sección.')
                return redirect('usuarios:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def login_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper