from django.urls import path
from . import views

app_name = "ordenes"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nueva/", views.crear, name="crear"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/cancelar/", views.eliminar, name="eliminar"),
    path("<int:pk>/estado/", views.cambiar_estado, name="cambiar_estado"),
    path("<int:pk>/agregar-servicio/", views.agregar_servicio, name="agregar_servicio"),
    path("<int:pk>/agregar-repuesto/", views.agregar_repuesto, name="agregar_repuesto"),
    path("<int:pk>/detalle/<int:det_pk>/eliminar/", views.eliminar_detalle, name="eliminar_detalle"),
    path("vehiculos-por-cliente/", views.vehiculos_por_cliente, name="vehiculos_por_cliente"),
]
