"""
Modelos de Mantenimiento Preventivo.
Programacion por kilometros y/o tiempo, con historial completo.
"""
from django.db import models
from django.conf import settings
from apps.vehiculos.models import Vehiculo


class TipoServicioMantenimiento(models.Model):
    """Catalogo de tipos de mantenimiento (cambio de aceite, frenos, etc.)."""

    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripcion")
    intervalo_km_recomendado = models.PositiveIntegerField(
        default=0,
        verbose_name="Intervalo recomendado (km)",
        help_text="0 = no aplica por km",
    )
    intervalo_dias_recomendado = models.PositiveIntegerField(
        default=0,
        verbose_name="Intervalo recomendado (dias)",
        help_text="0 = no aplica por tiempo",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de mantenimiento"
        verbose_name_plural = "Tipos de mantenimiento"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ProgramaMantenimiento(models.Model):
    """
    Programa de mantenimiento preventivo por vehiculo.
    Define cuando debe realizarse el proximo servicio.
    """

    class EstadoPrograma(models.TextChoices):
        AL_DIA = "AL_DIA", "Al dia"
        PROXIMO = "PROXIMO", "Proximo (en los proximos 500 km / 15 dias)"
        VENCIDO = "VENCIDO", "Vencido"

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name="programas_mantenimiento",
        verbose_name="Vehiculo",
    )
    tipo_servicio = models.ForeignKey(
        TipoServicioMantenimiento,
        on_delete=models.PROTECT,
        related_name="programas",
        verbose_name="Tipo de servicio",
    )
    # Ultimo servicio realizado
    ultimo_km = models.PositiveIntegerField(
        default=0, verbose_name="Kilometros en ultimo servicio"
    )
    ultima_fecha = models.DateField(
        null=True, blank=True, verbose_name="Fecha del ultimo servicio"
    )
    # Proximo servicio calculado
    proximo_km = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Proximo servicio (km)"
    )
    proxima_fecha = models.DateField(
        null=True, blank=True, verbose_name="Proxima fecha de servicio"
    )
    # Intervalos personalizados para este vehiculo
    intervalo_km = models.PositiveIntegerField(
        default=0, verbose_name="Intervalo personalizado (km)"
    )
    intervalo_dias = models.PositiveIntegerField(
        default=0, verbose_name="Intervalo personalizado (dias)"
    )
    estado = models.CharField(
        max_length=10,
        choices=EstadoPrograma.choices,
        default=EstadoPrograma.AL_DIA,
        verbose_name="Estado",
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Programa de mantenimiento"
        verbose_name_plural = "Programas de mantenimiento"
        unique_together = [["vehiculo", "tipo_servicio"]]
        ordering = ["proxima_fecha", "proximo_km"]

    def __str__(self):
        return f"{self.vehiculo.placa} — {self.tipo_servicio.nombre}"

    def actualizar_proximo(self):
        """Recalcula proximo_km y proxima_fecha segun intervalos."""
        from datetime import date, timedelta
        intervalo_km = self.intervalo_km or self.tipo_servicio.intervalo_km_recomendado
        intervalo_dias = self.intervalo_dias or self.tipo_servicio.intervalo_dias_recomendado
        if intervalo_km and self.ultimo_km:
            self.proximo_km = self.ultimo_km + intervalo_km
        if intervalo_dias and self.ultima_fecha:
            self.proxima_fecha = self.ultima_fecha + timedelta(days=intervalo_dias)


class HistorialMantenimiento(models.Model):
    """
    Registro historico de cada mantenimiento realizado al vehiculo.
    Se crea automaticamente al completar una OrdenTrabajo.
    """

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name="historial_mantenimiento",
        verbose_name="Vehiculo",
    )
    orden = models.ForeignKey(
        "ordenes.OrdenTrabajo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historial_mantenimiento",
        verbose_name="Orden de trabajo",
    )
    tipo_servicio = models.ForeignKey(
        TipoServicioMantenimiento,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="historial",
        verbose_name="Tipo de servicio",
    )
    descripcion = models.TextField(verbose_name="Descripcion del servicio realizado")
    km_al_servicio = models.PositiveIntegerField(
        default=0, verbose_name="Kilometraje al momento del servicio"
    )
    proximo_km_sugerido = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Proximo cambio sugerido (km)"
    )
    proxima_fecha_sugerida = models.DateField(
        null=True, blank=True, verbose_name="Proxima fecha sugerida"
    )
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historial_realizado",
        verbose_name="Tecnico",
    )
    costo = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Costo ($)"
    )
    fecha_servicio = models.DateField(verbose_name="Fecha del servicio")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de mantenimiento"
        verbose_name_plural = "Historial de mantenimiento"
        ordering = ["-fecha_servicio"]
        indexes = [
            models.Index(fields=["vehiculo"]),
            models.Index(fields=["fecha_servicio"]),
        ]

    def __str__(self):
        return f"{self.vehiculo.placa} — {self.descripcion[:50]} ({self.fecha_servicio})"
