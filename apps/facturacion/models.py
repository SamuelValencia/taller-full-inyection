"""
Modelos de Facturacion Interna.
Generacion de facturas internas para ordenes de trabajo.
"""
from django.db import models
from django.conf import settings
from apps.ordenes.models import OrdenTrabajo


class FacturaInterna(models.Model):
    """Factura interna para ordenes de trabajo."""

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EMITIDA = "EMITIDA", "Emitida"
        ANULADA = "ANULADA", "Anulada"

    numero_factura = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="N Factura",
        help_text="Generado automaticamente: FAC-YYYYMMDD-NNNN"
    )
    orden = models.OneToOneField(
        OrdenTrabajo,
        on_delete=models.PROTECT,
        related_name="factura",
        verbose_name="Orden de trabajo"
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name="Estado"
    )
    
    # Totales
    subtotal_mano_obra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Subtotal mano de obra ($)"
    )
    subtotal_repuestos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Subtotal repuestos ($)"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Subtotal ($)"
    )
    iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="IVA 15% ($)"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Total ($)"
    )
    
    # Observaciones
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    
    # Fechas
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de emision")
    fecha_anulacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de anulacion"
    )
    
    # Usuario que emite
    emitido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facturas_emitidas",
        verbose_name="Emitido por"
    )

    class Meta:
        verbose_name = "Factura interna"
        verbose_name_plural = "Facturas internas"
        ordering = ["-fecha_emision"]
        indexes = [
            models.Index(fields=["numero_factura"]),
            models.Index(fields=["orden"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["fecha_emision"]),
        ]

    def __str__(self):
        return f"{self.numero_factura} — {self.orden.numero_orden}"

    def save(self, *args, **kwargs):
        if not self.numero_factura:
            from datetime import date
            hoy = date.today().strftime("%Y%m%d")
            ultimo = FacturaInterna.objects.filter(
                numero_factura__startswith=f"FAC-{hoy}"
            ).count()
            self.numero_factura = f"FAC-{hoy}-{str(ultimo + 1).zfill(4)}"
        
        # Calcular totales si no estan establecidos
        if not self.subtotal_mano_obra:
            self.subtotal_mano_obra = self.orden.costo_mano_obra
        if not self.subtotal_repuestos:
            self.subtotal_repuestos = self.orden.costo_repuestos
        
        self.subtotal = self.subtotal_mano_obra + self.subtotal_repuestos
        self.iva = self.subtotal * 0.15
        self.total = self.subtotal + self.iva
        
        super().save(*args, **kwargs)

    def anular(self, usuario):
        """Anular la factura."""
        self.estado = self.Estado.ANULADA
        self.fecha_anulacion = models.timezone.now()
        self.save()
