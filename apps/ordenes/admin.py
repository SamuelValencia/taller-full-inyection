from django.contrib import admin

from .models import DetalleOrdenTrabajo, OrdenTrabajo


class DetalleOrdenTrabajoInline(admin.TabularInline):
    model = DetalleOrdenTrabajo
    extra = 1


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_orden",
        "cliente",
        "vehiculo",
        "servicio",
        "estado",
        "prioridad",
        "tipo_trabajo",
        "tecnico_asignado",
        "fecha_ingreso",
        "costo_total",
    )
    list_filter = ("estado", "prioridad", "tipo_trabajo", "servicio", "fecha_ingreso")
    search_fields = ("numero_orden", "vehiculo__placa", "cliente__apellidos", "servicio__nombre")
    inlines = [DetalleOrdenTrabajoInline]
    readonly_fields = ("numero_orden", "fecha_ingreso")
