from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("numero_documento", "apellidos", "nombres", "telefono", "email", "activo", "fecha_registro")
    list_filter = ("activo", "tipo_documento", "ciudad")
    search_fields = ("numero_documento", "nombres", "apellidos", "telefono", "email")
    ordering = ("apellidos", "nombres")
