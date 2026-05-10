from django.urls import path
from django.http import HttpResponse

app_name = 'reportes'

def temp(r): return HttpResponse('Próximamente - Reportes')

urlpatterns = [
    path('dashboard/', temp, name='dashboard'),
    path('exportar/',  temp, name='exportar'),
]