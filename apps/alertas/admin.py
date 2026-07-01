from django.contrib import admin

from .models import Alerta, PlantillaMensaje


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ("tipo", "nivel", "canal", "vehiculo", "destinatario", "leida", "activa", "programada_para", "fecha_creacion")
    list_filter = ("tipo", "nivel", "canal", "leida", "activa")
    search_fields = ("mensaje", "vehiculo__placa")


@admin.register(PlantillaMensaje)
class PlantillaMensajeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "canal", "activa", "fecha_actualizacion")
    list_filter = ("canal", "activa")
    search_fields = ("nombre", "asunto", "cuerpo")
