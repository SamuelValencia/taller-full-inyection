from django.contrib import admin
from .models import Servicio


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado", "fecha_actualizacion")
    list_filter = ("estado",)
    search_fields = ("nombre", "descripcion")
