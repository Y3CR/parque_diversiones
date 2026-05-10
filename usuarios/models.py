from django.contrib.auth.models import AbstractUser
from django.db import models

ROL_CHOICES = [
    ('administrador', 'Administrador'),
    ('taquilla', 'Taquilla'),
    ('operador_atraccion', 'Operador de Atracción'),
    ('operador_alimentos', 'Operador de Alimentos'),
    ('soporte', 'Soporte'),
]

class UsuarioInterno(AbstractUser):
    rol = models.CharField(max_length=30, choices=ROL_CHOICES, default='taquilla')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    def es_administrador(self):
        return self.rol == 'administrador'

    def es_taquilla(self):
        return self.rol == 'taquilla'

    def es_operador_atraccion(self):
        return self.rol == 'operador_atraccion'

    def es_operador_alimentos(self):
        return self.rol == 'operador_alimentos'

    def es_soporte(self):
        return self.rol == 'soporte'


class Visitante(models.Model):
    nombre = models.CharField(max_length=150)
    celular = models.CharField(max_length=15, unique=True)
    correo = models.EmailField(blank=True, null=True)
    documento = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.celular}"