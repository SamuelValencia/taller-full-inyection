"""
Admin configuration for Facturacion app.
"""
from django.contrib import admin
from .models import FacturaInterna


@admin.register(FacturaInterna)
class FacturaInternaAdmin(admin.ModelAdmin):
    list_display = [
        "numero_factura", "orden", "estado", "total", 
        "fecha_emision", "emitido_por"
    ]
    list_filter = ["estado", "fecha_emision"]
    search_fields = ["numero_factura", "orden__numero_orden"]
    readonly_fields = ["numero_factura", "fecha_emision", "subtotal", "iva", "total"]
    
    fieldsets = (
        ("Información General", {
            "fields": ("numero_factura", "orden", "estado")
        }),
        ("Totales", {
            "fields": (
                "subtotal_mano_obra", "subtotal_repuestos", 
                "subtotal", "iva", "total"
            )
        }),
        ("Observaciones", {
            "fields": ("observaciones",)
        }),
        ("Control", {
            "fields": ("emitido_por", "fecha_emision", "fecha_anulacion")
        }),
    )
