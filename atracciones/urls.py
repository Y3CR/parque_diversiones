from django.urls import path
from django.http import HttpResponse

app_name = 'atracciones'

def temp(r): return HttpResponse('Próximamente - Atracciones')

urlpatterns = [
    path('lista/',          temp, name='lista'),
    path('cambiar-estado/', temp, name='cambiar_estado'),
]