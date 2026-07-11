"""
Modelo de Usuario personalizado.
Extiende AbstractUser para agregar rol dinámico y datos del taller.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario del sistema con roles diferenciados.
    AbstractUser ya provee: username, first_name, last_name, email,
    is_staff, is_active, date_joined, password.
    """

    # Mantener las constantes para retrocompatibilidad en código existente
    class Rol(models.TextChoices):
        ADMINISTRADOR = "ADMIN", "Administrador"
        GERENTE = "GERENTE", "Gerente"
        MECANICO = "MECANICO", "Mecánico"
        RECEPCIONISTA = "RECEPCIONISTA", "Recepcionista"

    rol = models.ForeignKey(
        "roles.Rol",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios",
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
        rol_nombre = self.rol.nombre if self.rol else "Sin rol"
        return f"{self.get_full_name()} ({rol_nombre})"

    @property
    def rol_codigo(self):
        return self.rol.codigo if self.rol else ""

    def get_rol_display(self):
        return self.rol.nombre if self.rol else "Sin rol"

    @property
    def es_gerente(self):
        return self.rol_codigo == "GERENTE"

    @property
    def es_admin(self):
        return self.rol_codigo == "ADMIN" or self.is_superuser

    @property
    def es_mecanico(self):
        return self.rol_codigo == "MECANICO"

    @property
    def es_recepcionista(self):
        return self.rol_codigo == "RECEPCIONISTA"

    def tiene_permiso(self, modulo_codigo, accion_codigo):
        if self.is_superuser:
            return True
        if not self.rol:
            return False
        cache_key = f"_permisos_cache"
        if not hasattr(self, cache_key):
            permisos = set(
                self.rol.acciones.values_list("modulo__codigo", "codigo")
            )
            setattr(self, cache_key, permisos)
        return (modulo_codigo, accion_codigo) in getattr(self, cache_key)
