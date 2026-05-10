from django.urls import path
from . import views

app_name = 'atracciones'

urlpatterns = [
    path('lista/',                      views.lista_atracciones, name='lista'),
    path('crear/',                      views.crear_atraccion,   name='crear'),
    path('editar/<int:pk>/',            views.editar_atraccion,  name='editar'),
    path('estado/<int:pk>/',            views.cambiar_estado,    name='cambiar_estado'),
    path('toggle/<int:pk>/',            views.toggle_activa,     name='toggle'),
    path('categorias/',                 views.lista_categorias,  name='categorias'),
    path('categorias/crear/',           views.crear_categoria,   name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria,  name='editar_categoria'),
]