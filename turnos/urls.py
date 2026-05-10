from django.urls import path
from django.http import HttpResponse

app_name = 'turnos'

def temp(r): return HttpResponse('Próximamente - Turnos')

urlpatterns = [
    path('panel-admin/',    temp, name='panel_admin'),
    path('panel-operador/', temp, name='panel_operador'),
]