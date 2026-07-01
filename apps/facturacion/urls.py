"""
URL configuration for Facturacion app.
"""
from django.urls import path
from . import views

app_name = "facturacion"

urlpatterns = [
    path("", views.lista_facturas, name="lista"),
    path("crear/<int:orden_pk>/", views.crear_factura, name="crear"),
    path("<int:pk>/", views.detalle_factura, name="detalle"),
    path("<int:pk>/pdf/", views.factura_pdf, name="pdf"),
    path("<int:pk>/anular/", views.anular_factura, name="anular"),
]
