from django.apps import AppConfig


class OrdenesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ordenes"
    verbose_name = "Órdenes de servicio"

    def ready(self):
        import apps.ordenes.signals  # noqa: F401
