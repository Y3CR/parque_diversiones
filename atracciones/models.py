from django.db import models

ESTADO_ATRACCION = [
    ('abierta', 'Abierta'),
    ('cerrada', 'Cerrada'),
    ('mantenimiento', 'En mantenimiento'),
    ('suspendida', 'Suspendida por clima'),
    ('capacidad_limitada', 'Capacidad limitada'),
]

class CategoriaAtraccion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class Atraccion(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='atracciones/', blank=True, null=True)
    categoria = models.ForeignKey(CategoriaAtraccion, on_delete=models.SET_NULL, null=True)
    capacidad_por_ciclo = models.PositiveIntegerField(default=10)
    duracion_promedio = models.PositiveIntegerField(help_text='Duración en minutos', default=5)
    ubicacion = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=30, choices=ESTADO_ATRACCION, default='abierta')
    edad_minima = models.PositiveIntegerField(default=0, blank=True, null=True)
    estatura_minima = models.PositiveIntegerField(default=0, help_text='En centímetros', blank=True, null=True)
    restricciones = models.TextField(blank=True)
    horario_apertura = models.TimeField(blank=True, null=True)
    horario_cierre = models.TimeField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    def esta_disponible(self):
        return self.estado == 'abierta' and self.activa