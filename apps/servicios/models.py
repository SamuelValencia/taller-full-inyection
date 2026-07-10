from django.db import models


class Servicio(models.Model):
    class Categoria(models.TextChoices):
        MANTENIMIENTO_PREVENTIVO = "MANTENIMIENTO_PREVENTIVO", "Mantenimiento Preventivo"
        MECANICA_GENERAL = "MECANICA_GENERAL", "Mecanica General"
        INYECCION = "INYECCION", "Inyeccion"
        ELECTRICIDAD = "ELECTRICIDAD", "Electricidad"
        SUSPENSION = "SUSPENSION", "Suspension"
        FRENOS = "FRENOS", "Frenos"
        DIAGNOSTICO = "DIAGNOSTICO", "Diagnostico"
        COLISION = "COLISION", "Colision"
        PINTURA = "PINTURA", "Pintura"

    nombre = models.CharField(max_length=120, unique=True, verbose_name="Nombre")
    categoria = models.CharField(
        max_length=30,
        choices=Categoria.choices,
        default=Categoria.MECANICA_GENERAL,
        verbose_name="Categoria"
    )
    descripcion = models.TextField(blank=True, verbose_name="Descripcion")
    estado = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["categoria", "nombre"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["categoria"]),
            models.Index(fields=["estado"]),
        ]

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.nombre}"


class ServicioRepuesto(models.Model):
    """Catálogo de repuestos sugeridos para cada servicio."""

    servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE,
        related_name="repuestos_sugeridos", verbose_name="Servicio",
    )
    repuesto = models.ForeignKey(
        "inventario.Repuesto", on_delete=models.CASCADE,
        related_name="servicios_sugeridos", verbose_name="Repuesto",
    )
    cantidad_sugerida = models.DecimalField(
        max_digits=8, decimal_places=2, default=1, verbose_name="Cantidad sugerida",
    )
    opcional = models.BooleanField(default=False, verbose_name="Es opcional")
    nota = models.CharField(max_length=200, blank=True, verbose_name="Nota")

    class Meta:
        verbose_name = "Repuesto sugerido"
        verbose_name_plural = "Repuestos sugeridos"
        unique_together = ("servicio", "repuesto")
        ordering = ["servicio", "opcional", "repuesto__nombre"]

    def __str__(self):
        return f"{self.servicio.nombre} → {self.repuesto.nombre} x{self.cantidad_sugerida}"
