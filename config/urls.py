from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('usuarios/',   include('usuarios.urls')),
    path('atracciones/', include('atracciones.urls')),
    path('entradas/',   include('entradas.urls')),
    path('turnos/',     include('turnos.urls')),
    path('reportes/',   include('reportes.urls')),
    #path('comprar/',    include(('entradas.urls','entradas')namespace='entradas_web')),
    path('',            include('portal.urls')),
    path('portal/', include('portal.urls')),
    path('comida/', include('comida.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)