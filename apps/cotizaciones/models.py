"""
Modelos de Cotizacion.
Presupuesto previo a la ejecucion de una orden de trabajo.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.vehiculos.models import Vehiculo
from apps.clientes.models import Cliente


class Cotizacion(models.Model):

    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        ENVIADA = "ENVIADA", "Enviada"
        APROBADA = "APROBADA", "Aprobada"
        RECHAZADA = "RECHAZADA", "Rechazada"

    numero_cotizacion = models.CharField(max_length=20, unique=True, verbose_name="N Cotizacion")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name="cotizaciones", verbose_name="Vehiculo")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="cotizaciones", verbose_name="Cliente")
    elaborado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="cotizaciones_elaboradas", verbose_name="Elaborado por",
    )
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.BORRADOR, verbose_name="Estado")
    descripcion = models.TextField(blank=True, verbose_name="Descripcion del trabajo")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creacion")
    fecha_envio = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de envio")
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de aprobacion")
    fecha_validez = models.DateField(null=True, blank=True, verbose_name="Valida hasta")
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento ($)")
    aplica_iva = models.BooleanField(default=False, verbose_name="Aplica IVA")
    porcentaje_iva = models.PositiveSmallIntegerField(default=15, verbose_name="Porcentaje IVA (%)")
    orden_generada = models.OneToOneField(
        "ordenes.OrdenTrabajo", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="cotizacion_origen", verbose_name="Orden de trabajo generada",
    )

    class Meta:
        verbose_name = "Cotizacion"
        verbose_name_plural = "Cotizaciones"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.numero_cotizacion} — {self.get_estado_display()}"

    @property
    def subtotal(self):
        return sum(d.subtotal for d in self.detalles.all())

    @property
    def base_con_descuento(self):
        return self.subtotal - self.descuento

    @property
    def iva_monto(self):
        return self.base_con_descuento * Decimal(self.porcentaje_iva) / Decimal("100")

    @property
    def total(self):
        return self.base_con_descuento + self.iva_monto

    def save(self, *args, **kwargs):
        if not self.numero_cotizacion:
            from datetime import date
            hoy = date.today().strftime("%Y%m%d")
            ultimo = Cotizacion.objects.filter(numero_cotizacion__startswith=f"COT-{hoy}").count()
            self.numero_cotizacion = f"COT-{hoy}-{str(ultimo + 1).zfill(4)}"
        super().save(*args, **kwargs)


class DetalleCotizacion(models.Model):

    class TipoDetalle(models.TextChoices):
        SERVICIO = "SERVICIO", "Servicio / Mano de obra"
        REPUESTO = "REPUESTO", "Repuesto / Material"

    cotizacion = models.ForeignKey(
        Cotizacion, on_delete=models.CASCADE, related_name="detalles", verbose_name="Cotizacion"
    )
    tipo = models.CharField(max_length=10, choices=TipoDetalle.choices, default=TipoDetalle.SERVICIO, verbose_name="Tipo")
    servicio = models.ForeignKey(
        "servicios.Servicio", on_delete=models.PROTECT, null=True, blank=True,
        related_name="detalles_cotizacion", verbose_name="Servicio del catalogo",
    )
    descripcion = models.CharField(max_length=200, verbose_name="Descripcion")
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario ($)")

    class Meta:
        verbose_name = "Detalle de cotizacion"
        verbose_name_plural = "Detalles de cotizacion"

    def __str__(self):
        return f"{self.descripcion} x{self.cantidad}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
