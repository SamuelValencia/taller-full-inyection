from django.contrib import admin
from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "marca", "modelo", "anio", "cliente", "kilometraje_actual", "activo")
    list_filter = ("activo", "marca", "tipo_vehiculo", "tipo_combustible")
    search_fields = ("placa", "marca", "modelo", "numero_vin", "cliente__apellidos")
    autocomplete_fields = ("cliente",)
