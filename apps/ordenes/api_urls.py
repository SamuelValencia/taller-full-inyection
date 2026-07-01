from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import OrdenTrabajoViewSet

router = DefaultRouter()
router.register(r"", OrdenTrabajoViewSet, basename="ordentrabajo")

urlpatterns = [
    path("", include(router.urls)),
]
