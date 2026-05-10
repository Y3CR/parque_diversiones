from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioInterno, Visitante

@admin.register(UsuarioInterno)
class UsuarioInternoAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'rol', 'activo', 'fecha_creacion']
    list_filter = ['rol', 'activo']
    fieldsets = UserAdmin.fieldsets + (
        ('Datos del parque', {'fields': ('rol', 'activo')}),
    )

@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'celular', 'correo', 'fecha_registro']
    search_fields = ['nombre', 'celular', 'correo']