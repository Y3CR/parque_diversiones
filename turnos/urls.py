from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    path('panel-admin/',              views.panel_admin,    name='panel_admin'),
    path('panel-operador/',           views.panel_operador, name='panel_operador'),
    path('operador/<int:pk>/',        views.gestionar_cola, name='gestionar_cola'),
    path('llamar/<int:pk>/',          views.llamar_turno,   name='llamar_turno'),
    path('estado/<int:pk>/',          views.cambiar_estado, name='cambiar_estado'),
]