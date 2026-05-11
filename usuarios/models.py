from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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


class PaseNitro(models.Model):
    TIPO_CHOICES = [
        ('diario', 'Diario'),
        ('por_usos', 'Por cantidad de usos'),
        ('por_atraccion', 'Por atracción'),
    ]
    visitante      = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name='pases_nitro')
    tipo           = models.CharField(max_length=20, choices=TIPO_CHOICES, default='por_usos')
    usos_totales   = models.PositiveIntegerField(default=3)
    usos_restantes = models.PositiveIntegerField(default=3)
    fecha_inicio   = models.DateField(default=timezone.now)
    fecha_fin      = models.DateField(null=True, blank=True)
    activo         = models.BooleanField(default=True)
    creado_por     = models.CharField(max_length=50, default='taquilla')

    def esta_vigente(self):
        hoy = timezone.now().date()
        if not self.activo:
            return False
        if self.usos_restantes <= 0:
            return False
        if self.fecha_fin and hoy > self.fecha_fin:
            return False
        return True

    def __str__(self):
        return f'Nitro {self.tipo} — {self.visitante} ({self.usos_restantes} usos)'