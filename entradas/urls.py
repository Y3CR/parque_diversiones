from django.urls import path
from django.http import HttpResponse

app_name = 'entradas'

def temp(r): return HttpResponse('Próximamente - Entradas')

urlpatterns = [
    path('tipos/',       temp, name='tipos'),
    path('precios/',     temp, name='precios'),
    path('promociones/', temp, name='promociones'),
    path('vender/',      temp, name='vender'),
    path('validar/',     temp, name='validar'),
    path('lista/',       temp, name='lista_entradas'),
]