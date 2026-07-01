from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "email", "rol", "activo", "date_joined")
    list_filter = ("rol", "activo", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email", "cedula")
    fieldsets = UserAdmin.fieldsets + (
        ("Datos del taller", {"fields": ("rol", "telefono", "cedula", "especialidad", "activo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Datos del taller", {"fields": ("rol", "telefono", "cedula")}),
    )
