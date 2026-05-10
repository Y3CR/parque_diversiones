from django.urls import path
from django.shortcuts import redirect

app_name = 'portal'

urlpatterns = [
    path('', lambda r: redirect('usuarios:login'), name='inicio'),
]