from django.db import models
from usuarios.models import Visitante
from atracciones.models import Atraccion

ESTADO_TURNO = [
    ('generado', 'Generado'),
    ('en_espera', 'En espera'),
    ('proximo', 'Próximo'),
    ('llamado', 'Llamado'),
    ('usado', 'Usado'),
    ('vencido', 'Vencido'),
    ('cancelado', 'Cancelado'),
]


class ReglaTurno(models.Model):
    atraccion = models.OneToOneField(Atraccion, on_delete=models.CASCADE, related_name='regla')
    max_turnos_por_visitante = models.PositiveIntegerField(default=2)
    ventana_llamado_minutos = models.PositiveIntegerField(default=10)
    bloqueo_por_no_presentacion = models.BooleanField(default=True)
    minutos_bloqueo = models.PositiveIntegerField(default=30)

    def __str__(self):
        return f"Regla - {self.atraccion.nombre}"


class Turno(models.Model):
    atraccion = models.ForeignKey(Atraccion, on_delete=models.CASCADE, related_name='turnos')
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name='turnos')
    numero = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_TURNO, default='generado')
    prioridad = models.BooleanField(default=False)
    hora_creacion = models.DateTimeField(auto_now_add=True)
    hora_estimada = models.DateTimeField(blank=True, null=True)
    hora_llamado = models.DateTimeField(blank=True, null=True)
    hora_vencimiento = models.DateTimeField(blank=True, null=True)
    hora_uso = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('atraccion', 'numero')
        ordering = ['numero']

    def __str__(self):
        return f"Turno #{self.numero} - {self.atraccion.nombre} - {self.visitante.nombre}"

    def posicion_en_fila(self):
        return Turno.objects.filter(
            atraccion=self.atraccion,
            estado__in=['generado', 'en_espera'],
            numero__lt=self.numero
        ).count() + 1