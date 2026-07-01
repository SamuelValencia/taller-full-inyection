from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    path("", views.index, name="index"),
    path("orden/<int:pk>/pdf/", views.orden_pdf, name="orden_pdf"),
    path("vehiculo/<int:pk>/historial/pdf/", views.historial_vehiculo_pdf, name="historial_vehiculo_pdf"),
    # Exportación Excel
    path("excel/clientes/", views.exportar_clientes_excel, name="exportar_clientes_excel"),
    path("excel/vehiculos/", views.exportar_vehiculos_excel, name="exportar_vehiculos_excel"),
    path("excel/ordenes/", views.exportar_ordenes_excel, name="exportar_ordenes_excel"),
    path("excel/inventario/", views.exportar_inventario_excel, name="exportar_inventario_excel"),
    # Reportes Gerenciales
    path("gerenciales/productividad/", views.productividad_taller, name="productividad"),
    path("gerenciales/servicios/", views.servicios_realizados, name="servicios"),
    path("gerenciales/mantenimientos/", views.reporte_mantenimientos, name="mantenimientos"),
]
