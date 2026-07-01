from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.dashboard.urls", namespace="dashboard")),
    path("auth/", include("apps.authentication.urls", namespace="authentication")),
    path("usuarios/", include("apps.usuarios.urls", namespace="usuarios")),
    path("clientes/", include("apps.clientes.urls", namespace="clientes")),
    path("vehiculos/", include("apps.vehiculos.urls", namespace="vehiculos")),
    path("ordenes/", include("apps.ordenes.urls", namespace="ordenes")),
    path("cotizaciones/", include("apps.cotizaciones.urls", namespace="cotizaciones")),
    path("mantenimiento/", include("apps.mantenimiento.urls", namespace="mantenimiento")),
    path("alertas/", include("apps.alertas.urls", namespace="alertas")),
    path("reportes/", include("apps.reportes.urls", namespace="reportes")),
    path("inventario/", include("apps.inventario.urls", namespace="inventario")),
    path("facturacion/", include("apps.facturacion.urls", namespace="facturacion")),
    path("servicios/", include("apps.servicios.urls", namespace="servicios")),
    # API REST
    path("api/v1/clientes/", include("apps.clientes.api_urls")),
    path("api/v1/vehiculos/", include("apps.vehiculos.api_urls")),
    path("api/v1/ordenes/", include("apps.ordenes.api_urls")),
    path("api/v1/inventario/", include("apps.inventario.api_urls")),
    path("api/v1/facturacion/", include("apps.facturacion.api_urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
