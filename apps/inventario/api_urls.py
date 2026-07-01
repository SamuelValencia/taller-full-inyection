from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CategoriaRepuestoViewSet, RepuestoViewSet

router = DefaultRouter()
router.register(r"categorias", CategoriaRepuestoViewSet, basename="categoriarepuesto")
router.register(r"repuestos", RepuestoViewSet, basename="repuesto")

urlpatterns = [
    path("", include(router.urls)),
]
