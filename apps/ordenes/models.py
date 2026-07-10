"""
Modelos de Ordenes de Trabajo.
Nucleo del sistema: registra cada intervencion en un vehiculo.
"""
from django.db import models
from django.conf import settings
from apps.vehiculos.models import Vehiculo
from apps.clientes.models import Cliente
from apps.servicios.models import Servicio


class OrdenTrabajo(models.Model):

    class Estado(models.TextChoices):
        RECIBIDA = "RECIBIDA", "Recibida"
        DIAGNOSTICO = "DIAGNOSTICO", "Diagnostico"
        COTIZADA = "COTIZADA", "Cotizada"
        APROBADA = "APROBADA", "Aprobada"
        EN_PROCESO = "EN_PROCESO", "En proceso"
        ESPERANDO_REPUESTOS = "ESPERANDO_REPUESTOS", "Esperando repuestos"
        FINALIZADA = "FINALIZADA", "Finalizada"
        ENTREGADA = "ENTREGADA", "Entregada"
        CANCELADA = "CANCELADA", "Cancelada"

    class Prioridad(models.TextChoices):
        BAJA = "BAJA", "Baja"
        MEDIA = "MEDIA", "Media"
        ALTA = "ALTA", "Alta"
        URGENTE = "URGENTE", "Urgente"

    class TipoTrabajo(models.TextChoices):
        MANTENIMIENTO_PREVENTIVO = "MANTENIMIENTO_PREVENTIVO", "Mantenimiento Preventivo"
        MECANICA_GENERAL = "MECANICA_GENERAL", "Mecanica General"
        COLISION_ENDEREZADA = "COLISION_ENDEREZADA", "Colision y Enderezada"
        PINTURA = "PINTURA", "Pintura"
        DIAGNOSTICO = "DIAGNOSTICO", "Diagnostico"

    numero_orden = models.CharField(
        max_length=20, unique=True, verbose_name="N Orden",
        help_text="Generado automaticamente: OT-YYYYMMDD-NNNN",
    )
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name="ordenes_trabajo", verbose_name="Vehiculo")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ordenes_trabajo", verbose_name="Cliente")
    servicio = models.ForeignKey(
        Servicio, on_delete=models.PROTECT, related_name="ordenes_trabajo",
        null=True, blank=True, verbose_name="Servicio",
    )
    tecnico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="ordenes_trabajo_asignadas", verbose_name="Tecnico asignado",
        limit_choices_to={"rol": "MECANICO"},
    )
    recepcionista = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="ordenes_trabajo_recibidas", verbose_name="Recepcionista",
    )
    estado = models.CharField(max_length=25, choices=Estado.choices, default=Estado.RECIBIDA, verbose_name="Estado")
    prioridad = models.CharField(max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA, verbose_name="Prioridad")
    tipo_trabajo = models.CharField(
        max_length=30, choices=TipoTrabajo.choices, default=TipoTrabajo.MECANICA_GENERAL, verbose_name="Tipo de trabajo"
    )
    kilometraje_ingreso = models.PositiveIntegerField(default=0, verbose_name="Kilometraje al ingreso")
    descripcion_problema = models.TextField(verbose_name="Sintomas reportados por el cliente")
    diagnostico = models.TextField(blank=True, verbose_name="Diagnostico tecnico")
    autorizacion_cliente = models.TextField(blank=True, verbose_name="Autorizacion del cliente")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    fecha_ingreso = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de ingreso")
    fecha_estimada_entrega = models.DateField(null=True, blank=True, verbose_name="Fecha estimada de entrega")
    fecha_entrega_real = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de entrega real")
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Precio del servicio ($)")
    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo mano de obra ($)")
    costo_repuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo repuestos ($)")
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento ($)")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Orden de trabajo"
        verbose_name_plural = "Ordenes de trabajo"
        ordering = ["-fecha_ingreso"]
        indexes = [
            models.Index(fields=["numero_orden"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["vehiculo"]),
            models.Index(fields=["cliente"]),
            models.Index(fields=["fecha_ingreso"]),
        ]

    def __str__(self):
        return f"{self.numero_orden} — {self.vehiculo.placa} ({self.get_estado_display()})"

    @property
    def costo_total(self):
        return self.costo_mano_obra + self.costo_repuestos - self.descuento

    def save(self, *args, **kwargs):
        if not self.numero_orden:
            from datetime import date
            hoy = date.today().strftime("%Y%m%d")
            ultimo = OrdenTrabajo.objects.filter(numero_orden__startswith=f"OT-{hoy}").count()
            self.numero_orden = f"OT-{hoy}-{str(ultimo + 1).zfill(4)}"
        super().save(*args, **kwargs)


class DetalleOrdenTrabajo(models.Model):
    """Lineas de trabajo / repuestos de una orden de trabajo."""

    class TipoDetalle(models.TextChoices):
        SERVICIO = "SERVICIO", "Servicio / Mano de obra"
        REPUESTO = "REPUESTO", "Repuesto / Material"

    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="detalles", verbose_name="Orden de trabajo")
    tipo = models.CharField(max_length=10, choices=TipoDetalle.choices, default=TipoDetalle.SERVICIO, verbose_name="Tipo")
    servicio = models.ForeignKey(
        Servicio, on_delete=models.PROTECT, null=True, blank=True,
        related_name="detalles_ordenes", verbose_name="Servicio del catalogo",
    )
    repuesto_inventario = models.ForeignKey(
        "inventario.Repuesto", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="detalles_ordenes", verbose_name="Repuesto del inventario",
    )
    descripcion = models.CharField(max_length=200, verbose_name="Descripcion")
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario ($)")

    class Meta:
        verbose_name = "Detalle de orden de trabajo"
        verbose_name_plural = "Detalles de orden de trabajo"

    def __str__(self):
        return f"{self.descripcion} x{self.cantidad}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
