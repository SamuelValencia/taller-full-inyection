from django.urls import path
from . import views

app_name = "alertas"

urlpatterns = [
    # Módulo principal: recordatorios de mantenimiento para clientes
    path("", views.lista, name="lista"),
    path("nuevo/", views.crear_registro, name="crear_registro"),
    path("<int:pk>/", views.detalle_registro, name="detalle_registro"),
    path("<int:pk>/reenviar/", views.reenviar_recordatorio, name="reenviar"),
    path("configuracion/", views.configuracion, name="configuracion"),

    # Compatibilidad alertas internas
    path("interna/<int:pk>/leida/", views.marcar_leida, name="marcar_leida"),
    path("interna/marcar-todas/", views.marcar_todas_leidas, name="marcar_todas"),
]
