from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/',                  views.vista_login,       name='login'),
    path('logout/',                 views.vista_logout,      name='logout'),
    path('dashboard/',              views.dashboard,         name='dashboard'),
    path('lista/',                  views.lista_usuarios,    name='lista_usuarios'),
    path('crear/',                  views.crear_usuario,     name='crear_usuario'),
    path('editar/<int:pk>/',        views.editar_usuario,    name='editar_usuario'),
    path('buscar-visitante/',       views.buscar_visitante,  name='buscar_visitante'),
]