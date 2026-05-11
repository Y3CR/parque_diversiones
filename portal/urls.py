from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('atracciones/', views.atracciones, name='atracciones'),
    path('turno/<int:pk>/', views.tomar_turno, name='tomar_turno'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path('nitro/', views.comprar_nitro, name='comprar_nitro'),
    path('salir/', views.salir, name='salir'),
]