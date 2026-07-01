"""
Modelo de Usuario personalizado.
Extiende AbstractUser para agregar rol y datos del taller.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario del sistema con roles diferenciados.
    AbstractUser ya provee: username, first_name, last_name, email,
    is_staff, is_active, date_joined, password.
    """

    class Rol(models.TextChoices):
        ADMINISTRADOR = "ADMIN", "Administrador"
        GERENTE = "GERENTE", "Gerente"
        MECANICO = "MECANICO", "Mecánico"
        RECEPCIONISTA = "RECEPCIONISTA", "Recepcionista"

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.RECEPCIONISTA,
        verbose_name="Rol",
    )
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    cedula = models.CharField(
        max_length=13, blank=True, verbose_name="Cédula / RUC"
    )
    especialidad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Especialidad",
        help_text="Aplica para mecánicos",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    @property
    def es_gerente(self):
        return self.rol == self.Rol.GERENTE

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMINISTRADOR

    @property
    def es_mecanico(self):
        return self.rol == self.Rol.MECANICO

    @property
    def es_recepcionista(self):
        return self.rol == self.Rol.RECEPCIONISTA
