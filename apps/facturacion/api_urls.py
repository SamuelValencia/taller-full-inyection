from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import FacturaInternaViewSet

router = DefaultRouter()
router.register(r"", FacturaInternaViewSet, basename="facturainterna")

urlpatterns = [
    path("", include(router.urls)),
]
