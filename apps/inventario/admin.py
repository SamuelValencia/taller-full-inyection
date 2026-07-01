"""
Admin configuration for Inventario app.
"""
from django.contrib import admin
from .models import CategoriaRepuesto, Repuesto, MovimientoInventario


@admin.register(CategoriaRepuesto)
class CategoriaRepuestoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activo", "fecha_creacion"]
    list_filter = ["activo"]
    search_fields = ["nombre", "descripcion"]


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = [
        "codigo", "nombre", "categoria", "stock_actual", 
        "stock_minimo", "precio_venta", "activo"
    ]
    list_filter = ["categoria", "activo"]
    search_fields = ["codigo", "nombre", "marca", "modelo"]
    list_editable = ["precio_venta", "activo"]
    
    fieldsets = (
        ("Información General", {
            "fields": ("codigo", "nombre", "descripcion", "categoria")
        }),
        ("Detalles del Producto", {
            "fields": ("marca", "modelo")
        }),
        ("Control de Stock", {
            "fields": ("stock_actual", "stock_minimo", "stock_maximo", "ubicacion")
        }),
        ("Precios", {
            "fields": ("precio_compra", "precio_venta")
        }),
        ("Estado", {
            "fields": ("activo",)
        }),
    )


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = [
        "repuesto", "tipo", "cantidad", "stock_anterior", 
        "stock_nuevo", "fecha_movimiento", "realizado_por"
    ]
    list_filter = ["tipo", "fecha_movimiento"]
    search_fields = ["repuesto__codigo", "repuesto__nombre", "motivo"]
    readonly_fields = ["fecha_movimiento"]
    
    def has_add_permission(self, request):
        return False  # Los movimientos se crean automáticamente
    
    def has_change_permission(self, request, obj=None):
        return False  # Los movimientos no se editan manualmente
