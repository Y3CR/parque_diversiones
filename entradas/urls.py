from django.urls import path
from . import views

app_name = 'entradas'

urlpatterns = [
    # Tipos de entrada
    path('tipos/',                  views.lista_tipos,      name='tipos'),
    path('tipos/crear/',            views.crear_tipo,       name='crear_tipo'),
    path('tipos/editar/<int:pk>/',  views.editar_tipo,      name='editar_tipo'),

    # Precios
    path('precios/',                views.lista_precios,    name='precios'),
    path('precios/crear/',          views.crear_precio,     name='crear_precio'),

    # Promociones
    path('promociones/',                    views.lista_promociones,  name='promociones'),
    path('promociones/crear/',              views.crear_promocion,    name='crear_promocion'),
    path('promociones/editar/<int:pk>/',    views.editar_promocion,   name='editar_promocion'),

    # Entradas
    path('vender/',                         views.vender_entrada,     name='vender'),
    path('validar/',                        views.validar_entrada,    name='validar'),
    path('compra/',                         views.compra_web,         name='compra_web'),
    path('lista/',                          views.lista_entradas,     name='lista_entradas'),
    path('detalle/<int:pk>/',               views.detalle_entrada,    name='detalle_entrada'),
    path('comprobante/<int:pk>/',           views.comprobante,        name='comprobante'),
    path('anular/<int:pk>/',                views.anular_entrada,     name='anular_entrada'),
]