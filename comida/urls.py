from django.urls import path
from . import views

app_name = 'comida'

urlpatterns = [
    # Portal visitante
    path('catalogo/', views.catalogo, name='catalogo'),
    path('pedir/<int:pk>/', views.hacer_pedido, name='hacer_pedido'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    # Operador alimentos
    path('panel/', views.panel_alimentos, name='panel_alimentos'),
    path('pedido/<int:pk>/estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
]