from django.urls import path
from . import views

app_name = "mantenimiento"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nuevo/", views.crear_programa, name="crear"),
    path("<int:pk>/editar/", views.editar_programa, name="editar"),
    path("historial/registrar/", views.registrar_historial, name="registrar_historial"),
    path("tipos/", views.tipos_servicio, name="tipos"),
    path("tipos/nuevo/", views.crear_tipo, name="crear_tipo"),
]
