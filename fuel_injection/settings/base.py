"""
Django settings – BASE
Sistema Web Fuel Injection
"""

from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros
    "rest_framework",
    "crispy_forms",
    "crispy_bootstrap5",
    "widget_tweaks",
    "django_filters",
    "corsheaders",
    # Apps propias
    "apps.authentication",
    "apps.roles",
    "apps.usuarios",
    "apps.clientes",
    "apps.vehiculos",
    "apps.ordenes",
    "apps.cotizaciones",
    "apps.mantenimiento",
    "apps.alertas",
    "apps.dashboard",
    "apps.reportes",
    "apps.inventario",
    "apps.servicios",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fuel_injection.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.alertas.context_processors.alertas_no_leidas",
            ],
        },
    },
]

WSGI_APPLICATION = "fuel_injection.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="fuel_injection"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

AUTH_USER_MODEL = "usuarios.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-ec"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_URL = "authentication:login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "authentication:login"

# ── Email (SMTP via Resend) ────────────────────────────────────
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.resend.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="resend")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@fuelinjection.com")

# Token de recuperación válido por 1 hora (3600 segundos)
PASSWORD_RESET_TIMEOUT = 3600

# WhatsApp Business / Twilio / Meta Cloud API
WHATSAPP_PROVIDER = config("WHATSAPP_PROVIDER", default="")
WHATSAPP_ACCOUNT_SID = config("WHATSAPP_ACCOUNT_SID", default="")
WHATSAPP_AUTH_TOKEN = config("WHATSAPP_AUTH_TOKEN", default="")
WHATSAPP_FROM_NUMBER = config("WHATSAPP_FROM_NUMBER", default="")
WHATSAPP_META_TOKEN = config("WHATSAPP_META_TOKEN", default="")
WHATSAPP_META_PHONE_NUMBER_ID = config("WHATSAPP_META_PHONE_NUMBER_ID", default="")

# Info del taller (disponible en templates via settings)
TALLER_NOMBRE = config("TALLER_NOMBRE", default="Fuel Injection")
TALLER_TELEFONO = config("TALLER_TELEFONO", default="")
TALLER_DIRECCION = config("TALLER_DIRECCION", default="Guayaquil, Ecuador")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
