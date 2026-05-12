from django.db import models
from usuarios.models import Visitante
import uuid


class Combo(models.Model):
    nombre       = models.CharField(max_length=150)
    descripcion  = models.TextField(blank=True)
    precio       = models.DecimalField(max_digits=10, decimal_places=2)
    imagen       = models.ImageField(upload_to='combos/', blank=True, null=True)
    disponible   = models.BooleanField(default=True)
    creado_en    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} — ${self.precio}'


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('recibido',    'Recibido'),
        ('preparacion', 'En preparación'),
        ('listo',       'Listo para reclamar'),
        ('entregado',   'Entregado'),
        ('cancelado',   'Cancelado'),
    ]
    visitante    = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name='pedidos')
    codigo       = models.CharField(max_length=10, unique=True, editable=False)
    estado       = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='recibido')
    total        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creado_en    = models.DateTimeField(auto_now_add=True)
    actualizado  = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Pedido {self.codigo} — {self.visitante.nombre} ({self.estado})'


class ItemPedido(models.Model):
    pedido    = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    combo     = models.ForeignKey(Combo, on_delete=models.PROTECT)
    cantidad  = models.PositiveIntegerField(default=1)
    subtotal  = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.combo.precio * self.cantidad
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.cantidad}x {self.combo.nombre}'