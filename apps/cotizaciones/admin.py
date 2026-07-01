from django.contrib import admin
from .models import Cotizacion, DetalleCotizacion


class DetalleCotizacionInline(admin.TabularInline):
    model = DetalleCotizacion
    extra = 1


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ("numero_cotizacion", "cliente", "vehiculo", "estado", "fecha_creacion", "total")
    list_filter = ("estado", "fecha_creacion")
    search_fields = ("numero_cotizacion", "cliente__apellidos", "vehiculo__placa")
    inlines = [DetalleCotizacionInline]
    readonly_fields = ("numero_cotizacion", "fecha_creacion")
