"""
Modelo Vehículo.
Cada vehículo pertenece a un cliente y tiene su historial de servicios.
"""
from django.db import models
from apps.clientes.models import Cliente


class Vehiculo(models.Model):

    class TipoCombustible(models.TextChoices):
        GASOLINA = "GASOLINA", "Gasolina"
        DIESEL = "DIESEL", "Diésel"
        HIBRIDO = "HIBRIDO", "Híbrido"
        ELECTRICO = "ELECTRICO", "Eléctrico"
        GAS = "GAS", "Gas"

    class TipoVehiculo(models.TextChoices):
        AUTOMOVIL = "AUTOMOVIL", "Automóvil"
        CAMIONETA = "CAMIONETA", "Camioneta"
        SUV = "SUV", "SUV"

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="vehiculos",
        verbose_name="Cliente",
    )
    placa = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Placa",
    )
    marca = models.CharField(max_length=60, verbose_name="Marca")
    modelo = models.CharField(max_length=80, verbose_name="Modelo")
    anio = models.PositiveSmallIntegerField(verbose_name="Año")
    color = models.CharField(max_length=40, blank=True, verbose_name="Color")
    tipo_vehiculo = models.CharField(
        max_length=15,
        choices=TipoVehiculo.choices,
        default=TipoVehiculo.AUTOMOVIL,
        verbose_name="Tipo de vehículo",
    )
    tipo_combustible = models.CharField(
        max_length=15,
        choices=TipoCombustible.choices,
        default=TipoCombustible.GASOLINA,
        verbose_name="Tipo de combustible",
    )
    numero_vin = models.CharField(
        max_length=17,
        blank=True,
        verbose_name="Número VIN",
        help_text="Vehicle Identification Number (17 caracteres)",
    )
    numero_motor = models.CharField(max_length=50, blank=True, verbose_name="N° Motor")
    kilometraje_actual = models.PositiveIntegerField(
        default=0, verbose_name="Kilometraje actual (km)"
    )
    cilindraje = models.CharField(max_length=20, blank=True, verbose_name="Cilindraje")
    transmision = models.CharField(
        max_length=20,
        blank=True,
        choices=[("MANUAL", "Manual"), ("AUTOMATICA", "Automática"), ("CVT", "CVT")],
        verbose_name="Transmisión",
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["placa"]
        indexes = [
            models.Index(fields=["placa"]),
            models.Index(fields=["cliente"]),
        ]

    def __str__(self):
        return f"{self.placa} — {self.marca} {self.modelo} ({self.anio})"

    @property
    def descripcion_corta(self):
        return f"{self.marca} {self.modelo} {self.anio}"
