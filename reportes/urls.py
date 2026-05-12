from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('',               views.dashboard,          name='dashboard'),
    path('turnos/',        views.reporte_turnos,     name='turnos'),
    path('comida/',        views.reporte_comida,     name='comida'),
    path('export/turnos/', views.exportar_turnos_csv, name='export_turnos'),
    path('export/comida/', views.exportar_comida_csv, name='export_comida'),
]