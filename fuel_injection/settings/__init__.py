from decouple import config

DJANGO_SETTINGS_MODULE = config(
    "DJANGO_SETTINGS_MODULE",
    default="fuel_injection.settings.development",
)
