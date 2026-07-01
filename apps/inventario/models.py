"""
Modelos de Inventario/Bodega.
Gestion de repuestos, control de stock y categorias.
"""
from django.db import models


class CategoriaRepuesto(models.Model):
    """Categorias para organizar el inventario de repuestos."""

    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripcion")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Creada el")

    class Meta:
        verbose_name = "Categoria de repuesto"
        verbose_name_plural = "Categorias de repuestos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Repuesto(models.Model):
    """Catalogo de repuestos disponibles en bodega."""

    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Codigo",
        help_text="Codigo unico del repuesto"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripcion")
    categoria = models.ForeignKey(
        CategoriaRepuesto,
        on_delete=models.PROTECT,
        related_name="repuestos",
        verbose_name="Categoria",
        null=True,
        blank=True
    )
    marca = models.CharField(max_length=100, blank=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, verbose_name="Modelo")
    
    # Control de stock
    stock_actual = models.PositiveIntegerField(default=0, verbose_name="Stock actual")
    stock_minimo = models.PositiveIntegerField(
        default=5,
        verbose_name="Stock minimo",
        help_text="Alerta cuando el stock baje de este valor"
    )
    stock_maximo = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Stock maximo",
        help_text="Stock maximo recomendado"
    )
    
    # Precios
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Precio de compra ($)"
    )
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Precio de venta ($)"
    )
    
    # Ubicacion
    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ubicacion en bodega",
        help_text="Ej: Estante A-3, Caja 2"
    )
    
    # Estado
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"
        ordering = ["categoria", "nombre"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["categoria"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def stock_bajo(self):
        """Verifica si el stock esta por debajo del minimo."""
        return self.stock_actual <= self.stock_minimo

    @property
    def valor_inventario(self):
        """Valor total del inventario de este repuesto."""
        return self.stock_actual * self.precio_compra


class MovimientoInventario(models.Model):
    """Registro de movimientos de entrada y salida de repuestos."""

    class TipoMovimiento(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"
        AJUSTE = "AJUSTE", "Ajuste"
        DEVOLUCION = "DEVOLUCION", "Devolucion"

    repuesto = models.ForeignKey(
        Repuesto,
        on_delete=models.CASCADE,
        related_name="movimientos",
        verbose_name="Repuesto"
    )
    tipo = models.CharField(
        max_length=15,
        choices=TipoMovimiento.choices,
        verbose_name="Tipo de movimiento"
    )
    cantidad = models.IntegerField(
        verbose_name="Cantidad",
        help_text="Positivo para entrada, negativo para salida"
    )
    stock_anterior = models.PositiveIntegerField(verbose_name="Stock anterior")
    stock_nuevo = models.PositiveIntegerField(verbose_name="Stock nuevo")
    
    # Referencia a documento
    orden_trabajo = models.ForeignKey(
        "ordenes.OrdenTrabajo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_inventario",
        verbose_name="Orden de trabajo"
    )
    
    motivo = models.TextField(blank=True, verbose_name="Motivo")
    realizado_por = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_realizados",
        verbose_name="Realizado por"
    )
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del movimiento")

    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ["-fecha_movimiento"]
        indexes = [
            models.Index(fields=["repuesto"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["fecha_movimiento"]),
        ]

    def __str__(self):
        return f"{self.tipo} {self.repuesto.codigo}: {self.cantidad} ({self.fecha_movimiento})"
