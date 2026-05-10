from django.db import models
from usuarios.models import UsuarioInterno, Visitante
import uuid

CANAL_VENTA = [
    ('web', 'Web'),
    ('taquilla', 'Taquilla'),
]

ESTADO_ENTRADA = [
    ('activa', 'Activa'),
    ('usada', 'Usada'),
    ('vencida', 'Vencida'),
    ('anulada', 'Anulada'),
]


class TipoEntrada(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Precio(models.Model):
    tipo_entrada = models.ForeignKey(TipoEntrada, on_delete=models.CASCADE, related_name='precios')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    canal = models.CharField(max_length=20, choices=CANAL_VENTA, default='web')
    vigencia_desde = models.DateField()
    vigencia_hasta = models.DateField(blank=True, null=True)
    valor_anterior = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    usuario_modifico = models.ForeignKey(UsuarioInterno, on_delete=models.SET_NULL, null=True)
    fecha_modificacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_entrada.nombre} - ${self.valor} ({self.canal})"


class Promocion(models.Model):
    nombre = models.CharField(max_length=150)
    tipo_entrada = models.ForeignKey(TipoEntrada, on_delete=models.CASCADE)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    vigencia_desde = models.DateField()
    vigencia_hasta = models.DateField()
    canal = models.CharField(max_length=20, choices=CANAL_VENTA, default='taquilla')
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.descuento_porcentaje}%"


class Entrada(models.Model):
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE, related_name='entradas')
    tipo_entrada = models.ForeignKey(TipoEntrada, on_delete=models.SET_NULL, null=True)
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_ENTRADA, default='activa')
    codigo_validacion = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    canal_venta = models.CharField(max_length=20, choices=CANAL_VENTA, default='web')
    fecha_compra = models.DateTimeField(auto_now_add=True)
    fecha_uso = models.DateField(blank=True, null=True)
    vendido_por = models.ForeignKey(UsuarioInterno, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Entrada {self.codigo_validacion} - {self.visitante.nombre}"

    def codigo_str(self):
        return str(self.codigo_validacion).upper().replace('-', '')[:10]


class AuditoriaAnulacion(models.Model):
    TIPO_ELEMENTO = [
        ('entrada', 'Entrada'),
        ('turno', 'Turno'),
        ('pedido', 'Pedido'),
        ('pase_nitro', 'Pase Nitro'),
    ]
    elemento_tipo = models.CharField(max_length=20, choices=TIPO_ELEMENTO)
    elemento_id = models.PositiveIntegerField()
    usuario = models.ForeignKey(UsuarioInterno, on_delete=models.SET_NULL, null=True)
    rol_usuario = models.CharField(max_length=30)
    motivo = models.TextField()
    estado_anterior = models.CharField(max_length=30)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anulación {self.elemento_tipo} #{self.elemento_id} por {self.usuario}"