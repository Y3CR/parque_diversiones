from django.db import models
from usuarios.models import Visitante

TIPO_EVENTO_SMS = [
    ('turno_llamado', 'Turno llamado'),
    ('pedido_listo', 'Pedido listo para reclamar'),
    ('pedido_entregado', 'Pedido entregado'),
    ('atraccion_cerrada', 'Atracción cerrada'),
]

ESTADO_ENTREGA = [
    ('enviado', 'Enviado'),
    ('fallido', 'Fallido'),
    ('pendiente', 'Pendiente'),
]


class HistorialSMS(models.Model):
    visitante = models.ForeignKey(Visitante, on_delete=models.SET_NULL, null=True)
    celular = models.CharField(max_length=15)
    mensaje = models.TextField()
    tipo_evento = models.CharField(max_length=30, choices=TIPO_EVENTO_SMS)
    estado_entrega = models.CharField(max_length=20, choices=ESTADO_ENTREGA, default='pendiente')
    fecha_envio = models.DateTimeField(auto_now_add=True)
    referencia_externa = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"SMS {self.tipo_evento} → {self.celular} ({self.estado_entrega})"