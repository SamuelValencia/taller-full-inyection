"""
Modelo Cliente.
Persona natural o jurídica propietaria de uno o más vehículos.
"""
from django.db import models


class Cliente(models.Model):
    """Datos personales del propietario del vehículo."""

    class TipoDocumento(models.TextChoices):
        CEDULA = "CEDULA", "Cédula"
        RUC = "RUC", "RUC"
        PASAPORTE = "PASAPORTE", "Pasaporte"

    tipo_documento = models.CharField(
        max_length=10,
        choices=TipoDocumento.choices,
        default=TipoDocumento.CEDULA,
        verbose_name="Tipo de documento",
    )
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de documento",
    )
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Correo electrónico")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    ciudad = models.CharField(max_length=80, default="Guayaquil", verbose_name="Ciudad")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["apellidos", "nombres"]
        indexes = [
            models.Index(fields=["numero_documento"]),
            models.Index(fields=["apellidos", "nombres"]),
        ]

    def __str__(self):
        return f"{self.apellidos} {self.nombres} — {self.numero_documento}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def total_vehiculos(self):
        return self.vehiculos.filter(activo=True).count()
