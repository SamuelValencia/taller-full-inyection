"""
Módulo de Alertas — Sistema de recordatorios de mantenimiento para clientes.
"""
from django.db import models
from django.conf import settings
from apps.vehiculos.models import Vehiculo
from apps.clientes.models import Cliente


# ──────────────────────────────────────────────────────────────
# Modelos internos originales (mantener para el context processor)
# ──────────────────────────────────────────────────────────────

class Alerta(models.Model):
    class Canal(models.TextChoices):
        INTERNA = "INTERNA", "Interna"
        EMAIL = "EMAIL", "Correo electrónico"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        AMBOS = "AMBOS", "Correo y WhatsApp"

    class TipoAlerta(models.TextChoices):
        PROXIMO_MANTENIMIENTO = "PROX_MANT", "Próximo mantenimiento"
        MANTENIMIENTO_VENCIDO = "MANT_VENC", "Mantenimiento vencido"
        ORDEN_PENDIENTE = "ORD_PEND", "Orden pendiente"
        VEHICULO_LISTO = "VEH_LISTO", "Vehículo listo para entrega"
        RETRASO = "RETRASO", "Retraso en entrega"
        RECORDATORIO = "RECORDATORIO", "Recordatorio general"

    class Nivel(models.TextChoices):
        INFO = "INFO", "Información"
        WARNING = "WARNING", "Advertencia"
        DANGER = "DANGER", "Urgente"

    tipo = models.CharField(max_length=15, choices=TipoAlerta.choices, verbose_name="Tipo de alerta")
    nivel = models.CharField(max_length=10, choices=Nivel.choices, default=Nivel.INFO, verbose_name="Nivel")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True, blank=True, related_name="alertas", verbose_name="Vehículo")
    orden = models.ForeignKey("ordenes.OrdenTrabajo", on_delete=models.CASCADE, null=True, blank=True, related_name="alertas", verbose_name="Orden de trabajo")
    mensaje = models.TextField(verbose_name="Mensaje")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Creada el")
    fecha_vencimiento = models.DateTimeField(null=True, blank=True, verbose_name="Vence el")
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="alertas_recibidas", verbose_name="Destinatario")
    leida = models.BooleanField(default=False, verbose_name="Leída")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    canal = models.CharField(max_length=10, choices=Canal.choices, default=Canal.INTERNA, verbose_name="Canal de envío")
    programada_para = models.DateTimeField(null=True, blank=True, verbose_name="Programada para")
    enviada_email = models.BooleanField(default=False, verbose_name="Enviada por correo")
    enviada_whatsapp = models.BooleanField(default=False, verbose_name="Enviada por WhatsApp")
    ultimo_error_envio = models.TextField(blank=True, verbose_name="Último error de envío")

    class Meta:
        verbose_name = "Alerta interna"
        verbose_name_plural = "Alertas internas"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["leida", "activa"]),
            models.Index(fields=["destinatario"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["canal", "programada_para"]),
        ]

    def __str__(self):
        return f"[{self.get_nivel_display()}] {self.get_tipo_display()} — {self.mensaje[:60]}"


class PlantillaMensaje(models.Model):
    class Canal(models.TextChoices):
        EMAIL = "EMAIL", "Correo electrónico"
        WHATSAPP = "WHATSAPP", "WhatsApp"

    nombre = models.CharField(max_length=120, unique=True, verbose_name="Nombre")
    canal = models.CharField(max_length=10, choices=Canal.choices, verbose_name="Canal")
    asunto = models.CharField(max_length=180, blank=True, verbose_name="Asunto")
    cuerpo = models.TextField(verbose_name="Cuerpo")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plantilla de mensaje"
        verbose_name_plural = "Plantillas de mensajes"
        ordering = ["canal", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_canal_display()})"


# ──────────────────────────────────────────────────────────────
# NUEVOS modelos: Sistema de recordatorios para clientes
# ──────────────────────────────────────────────────────────────

class ConfiguracionRecordatorio(models.Model):
    """Configuración global del sistema de recordatorios de mantenimiento."""
    dias_anticipacion = models.PositiveIntegerField(
        default=5,
        verbose_name="Días de anticipación",
        help_text="Cuántos días antes del mantenimiento enviar el recordatorio.",
    )
    activo = models.BooleanField(default=True, verbose_name="Sistema activo")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de recordatorio"
        verbose_name_plural = "Configuración de recordatorios"

    def __str__(self):
        return f"Config: {self.dias_anticipacion} días de anticipación"

    @classmethod
    def obtener(cls):
        """Retorna la configuración activa o crea una por defecto."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class RegistroMantenimiento(models.Model):
    """
    Registra cada mantenimiento realizado a un vehículo y programa el siguiente.
    Se crea automáticamente cuando una OT de tipo MANTENIMIENTO_PREVENTIVO
    pasa a estado FINALIZADA.
    """

    class TipoIntervalo(models.TextChoices):
        DIAS = "DIAS", "Por tiempo (días)"
        KM = "KM", "Por kilometraje"
        AMBOS = "AMBOS", "Por tiempo y kilometraje"

    class CanalEnvio(models.TextChoices):
        EMAIL = "EMAIL", "Correo electrónico"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        AMBOS = "AMBOS", "Correo y WhatsApp"

    orden = models.OneToOneField(
        "ordenes.OrdenTrabajo",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="registro_mantenimiento",
        verbose_name="Orden de trabajo",
    )
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT,
        related_name="registros_mantenimiento",
        verbose_name="Vehículo",
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT,
        related_name="registros_mantenimiento",
        verbose_name="Cliente",
    )
    tipo_mantenimiento = models.CharField(
        max_length=120,
        verbose_name="Tipo de mantenimiento",
        default="Mantenimiento preventivo",
    )
    descripcion_trabajos = models.TextField(
        blank=True,
        verbose_name="Descripción de los trabajos realizados",
    )
    fecha_mantenimiento = models.DateField(verbose_name="Fecha del mantenimiento")
    kilometraje_mantenimiento = models.PositiveIntegerField(
        default=0, verbose_name="Kilometraje al momento del mantenimiento (km)"
    )

    # Intervalo para el próximo mantenimiento
    tipo_intervalo = models.CharField(
        max_length=5,
        choices=TipoIntervalo.choices,
        default=TipoIntervalo.DIAS,
        verbose_name="Tipo de intervalo",
    )
    intervalo_dias = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Intervalo en días",
        help_text="Ej: 60 = cada 2 meses, 90 = cada 3 meses",
    )
    intervalo_km = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Intervalo en kilómetros",
        help_text="Ej: 5000, 10000",
    )
    fecha_proximo_mantenimiento = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha del próximo mantenimiento",
    )
    kilometraje_proximo_mantenimiento = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Kilometraje del próximo mantenimiento (km)",
    )

    # Canal de envío del recordatorio
    canal_envio = models.CharField(
        max_length=10,
        choices=CanalEnvio.choices,
        default=CanalEnvio.EMAIL,
        verbose_name="Canal de envío del recordatorio",
    )

    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de mantenimiento"
        verbose_name_plural = "Registros de mantenimiento"
        ordering = ["-fecha_mantenimiento"]
        indexes = [
            models.Index(fields=["vehiculo"]),
            models.Index(fields=["cliente"]),
            models.Index(fields=["fecha_proximo_mantenimiento"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self):
        return f"{self.vehiculo.placa} — {self.tipo_mantenimiento} ({self.fecha_mantenimiento})"

    @property
    def dias_para_proximo(self):
        """Días que faltan para el próximo mantenimiento."""
        if not self.fecha_proximo_mantenimiento:
            return None
        from django.utils import timezone
        hoy = timezone.localdate()
        delta = (self.fecha_proximo_mantenimiento - hoy).days
        return delta

    @property
    def estado_semaforo(self):
        """
        'verde' > 10 días | 'amarillo' <= 10 días | 'rojo' <= 0 (vencido)
        """
        dias = self.dias_para_proximo
        if dias is None:
            return "secondary"
        if dias < 0:
            return "danger"
        if dias <= 5:
            return "warning"
        if dias <= 10:
            return "info"
        return "success"

    def calcular_proximo(self):
        """Calcula y guarda la fecha/km del próximo mantenimiento."""
        from datetime import timedelta
        if self.tipo_intervalo in ("DIAS", "AMBOS") and self.intervalo_dias:
            self.fecha_proximo_mantenimiento = (
                self.fecha_mantenimiento + timedelta(days=self.intervalo_dias)
            )
        if self.tipo_intervalo in ("KM", "AMBOS") and self.intervalo_km:
            self.kilometraje_proximo_mantenimiento = (
                self.kilometraje_mantenimiento + self.intervalo_km
            )


class RecordatorioMantenimiento(models.Model):
    """
    Registro de cada recordatorio enviado (o pendiente de envío) a un cliente.
    Un RegistroMantenimiento puede tener múltiples recordatorios
    (reenvíos incluidos).
    """

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente de envío"
        ENVIADO = "ENVIADO", "Enviado correctamente"
        ERROR = "ERROR", "Error en el envío"
        CANCELADO = "CANCELADO", "Cancelado"

    class Canal(models.TextChoices):
        EMAIL = "EMAIL", "Correo electrónico"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        AMBOS = "AMBOS", "Correo y WhatsApp"

    registro = models.ForeignKey(
        RegistroMantenimiento,
        on_delete=models.CASCADE,
        related_name="recordatorios",
        verbose_name="Registro de mantenimiento",
    )
    canal = models.CharField(
        max_length=10,
        choices=Canal.choices,
        verbose_name="Canal de envío",
    )
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name="Estado",
    )
    fecha_programada = models.DateField(
        verbose_name="Fecha programada para envío",
        help_text="Se calcula: fecha_proximo - días de anticipación",
    )
    fecha_envio = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha y hora de envío real"
    )
    enviado_email = models.BooleanField(default=False, verbose_name="Email enviado")
    enviado_whatsapp = models.BooleanField(default=False, verbose_name="WhatsApp enviado")
    error_detalle = models.TextField(blank=True, verbose_name="Detalle del error")
    intento_numero = models.PositiveIntegerField(default=1, verbose_name="N° de intento")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    class Meta:
        verbose_name = "Recordatorio de mantenimiento"
        verbose_name_plural = "Recordatorios de mantenimiento"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["fecha_programada"]),
            models.Index(fields=["registro"]),
        ]

    def __str__(self):
        return (
            f"Recordatorio {self.get_canal_display()} — "
            f"{self.registro.cliente.nombre_completo} "
            f"({self.get_estado_display()})"
        )
