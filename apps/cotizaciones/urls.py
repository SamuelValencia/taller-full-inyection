from django.urls import path
from . import views

app_name = "cotizaciones"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nueva/", views.crear, name="crear"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/aprobar/", views.aprobar, name="aprobar"),
    path("<int:pk>/agregar-servicio/", views.agregar_servicio, name="agregar_servicio"),
    path("<int:pk>/agregar-repuesto/", views.agregar_repuesto, name="agregar_repuesto"),
    path("<int:pk>/convertir-orden/", views.convertir_orden, name="convertir_orden"),
    path("<int:pk>/pdf/", views.pdf, name="pdf"),
    path("<int:pk>/enviar/", views.enviar_notificacion, name="enviar_notificacion"),
    path("<int:pk>/detalle/<int:det_pk>/eliminar/", views.eliminar_detalle, name="eliminar_detalle"),
    path("<int:pk>/detalle/<int:det_pk>/editar/", views.editar_detalle, name="editar_detalle"),
]
