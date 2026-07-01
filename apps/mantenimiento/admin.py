from django.contrib import admin
from .models import TipoServicioMantenimiento, ProgramaMantenimiento, HistorialMantenimiento


@admin.register(TipoServicioMantenimiento)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "intervalo_km_recomendado", "intervalo_dias_recomendado", "activo")
    search_fields = ("nombre",)


@admin.register(ProgramaMantenimiento)
class ProgramaMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "tipo_servicio", "ultimo_km", "proximo_km", "proxima_fecha", "estado")
    list_filter = ("estado", "tipo_servicio")
    search_fields = ("vehiculo__placa",)


@admin.register(HistorialMantenimiento)
class HistorialMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "tipo_servicio", "km_al_servicio", "fecha_servicio", "tecnico", "costo")
    list_filter = ("fecha_servicio", "tipo_servicio")
    search_fields = ("vehiculo__placa", "descripcion")
