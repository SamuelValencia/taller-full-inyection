from django.db import models


class Modulo(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=60, default="fas fa-circle")
    url_name = models.CharField(max_length=100, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"

    def __str__(self):
        return self.nombre


class Accion(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="acciones")
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("modulo", "codigo")
        ordering = ["modulo__orden", "codigo"]
        verbose_name = "Acción"
        verbose_name_plural = "Acciones"

    def __str__(self):
        return f"{self.modulo.codigo}.{self.codigo}"


class Rol(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    acciones = models.ManyToManyField(Accion, blank=True, related_name="roles")
    activo = models.BooleanField(default=True)
    es_sistema = models.BooleanField(
        default=False,
        help_text="Los roles de sistema no pueden eliminarse."
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.nombre

    def tiene_permiso(self, modulo_codigo, accion_codigo):
        return self.acciones.filter(
            modulo__codigo=modulo_codigo,
            codigo=accion_codigo
        ).exists()

    def puede_eliminarse(self):
        return not self.es_sistema and not self.usuarios.exists()
