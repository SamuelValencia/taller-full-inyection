from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import VehiculoViewSet

router = DefaultRouter()
router.register(r"", VehiculoViewSet, basename="vehiculo")

urlpatterns = [
    path("", include(router.urls)),
]
